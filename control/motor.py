# -*- coding: utf-8 -*-
"""
motor.py -- Batería forense de control interno (funciones puras, sin base de datos).

Cada prueba mira un libro de asientos y propone candidatos a revisión. Ninguna acusa:
un candidato no es una condena, es algo que un humano debe mirar. La otra mitad del
valor de cada prueba está en su CONTROL NEGATIVO: la lista de lo que NO se marca, para
no ahogar al auditor en falsos positivos. Un detector sin control negativo grita sin parar.

Pruebas (código puro, aritmética determinista, sin dependencias):
  Benford         primer dígito de los importes contra la curva de Benford.
  Redondos        concentración anómala de importes redondos por cuenta, nunca uno aislado.
  Fantasma        cuenta de tercero que mueve dinero sin ningún rastro documental.
  Duplicados      la misma línea exacta repetida (referencia, cuenta, debe, haber).
  Fraccionamiento importes parecidos al mismo tercero en pocos días (partir un pago grande).
  Casi-duplicado  el pago repetido que se escapa por un céntimo o por referencia distinta.
  Coherencia      vencimiento o cobro anteriores a la fecha del asiento (imposible en el tiempo).
  Huecos          saltos en la numeración de asientos (informativo, calidad de dato).

Extraído y saneado del motor interno de TechAcces. Sin conexión, sin credenciales,
sin datos reales. Solo la lógica.
"""

import math
from datetime import datetime, date


# ---------------------------------------------------------------------------
# Constantes de la profesión y umbrales (revisable, no dogma)
# ---------------------------------------------------------------------------

# Distribución de Benford del primer dígito (1..9), en proporción.
BENFORD_1D = {d: math.log10(1 + 1.0 / d) for d in range(1, 10)}

# Gate de tamaño de la profesión (Journal of Accountancy, 2022: por debajo de 5.000
# registros la prueba de Benford no se considera fiable). Se aplica al subconjunto
# de importes elegidos a mano, que es donde un defraudador dejaría huella.
BENFORD_MIN_REGISTROS = 5000

# Redondos: umbral de concentración por cuenta.
REDONDOS_RATIO_ALERTA = 0.10   # más del 10 por ciento de redondos en la cuenta
REDONDOS_MIN_EN_SEGMENTO = 5   # y al menos 5 redondos (evita el ruido de muestra pequeña)

# Cuentas donde el importe redondo es esperado por naturaleza (provisión 14x, deuda a
# largo plazo 16x/17x, amortización acumulada 28x, dotación de amortización 68x). Se
# excluyen a propósito para no gritar sobre lo normal. Exclusión revisable, no dogma.
CUENTAS_REDONDAS_POR_NATURALEZA = ("14", "16", "17", "28", "68")

# Fraccionamiento: parámetros del clúster.
FRACC_VENTANA_DIAS = 7         # ventana temporal del clúster
FRACC_BANDA_PCT = 0.10         # importes "similares" entre sí (mas o menos 10 por ciento)
FRACC_MIN_N = 3                # al menos 3 líneas para hablar de fraccionamiento
FRACC_UMBRAL_SUMA = 1000.0     # y suma del clúster por encima de este umbral

# Referencias de pagos recurrentes legítimos (nóminas): control negativo de fraccionamiento.
REF_RECURRENTE = ("NOM-", "PAGNOM-")

# Casi-duplicado: tolerancia y ventana.
CASIDUP_TOL_ABS = 0.05         # euros de tolerancia para "el mismo importe" (capta el céntimo)
CASIDUP_VENTANA_DIAS = 7       # ventana de fechas del clúster

# Tipos de operación que son entradas de sistema (control negativo transversal):
# apertura, cierre y regularización mueven cuentas sin documento por diseño.
TIPOS_SISTEMA = ("APERTURA", "CIERRE", "FISCAL", "ANULACION")


# ---------------------------------------------------------------------------
# Benford
# ---------------------------------------------------------------------------

def benford_chi2(observado: dict, n: int) -> float:
    """Chi-cuadrado del primer dígito contra Benford. observado = {dígito(int): conteo}."""
    if n <= 0:
        return 0.0
    chi2 = 0.0
    for d in range(1, 10):
        esperado = BENFORD_1D[d] * n
        obs = observado.get(d, 0)
        if esperado > 0:
            chi2 += (obs - esperado) ** 2 / esperado
    return chi2


def benford_mad(observado: dict, n: int) -> float:
    """Desviación absoluta media (MAD), en puntos de proporción, contra Benford."""
    if n <= 0:
        return 0.0
    total = 0.0
    for d in range(1, 10):
        obs_pct = observado.get(d, 0) / n
        total += abs(obs_pct - BENFORD_1D[d])
    return total / 9.0


def decision_gate_benford(n_manual: int) -> str:
    """NO_APLICA si el subconjunto manual no llega al mínimo de la profesión; APLICA si sí."""
    return "APLICA" if n_manual >= BENFORD_MIN_REGISTROS else "NO_APLICA"


def primer_digito(importe) -> int:
    """Primer dígito significativo de un importe (>=1). Devuelve 0 si no aplica."""
    try:
        v = abs(float(importe))
    except (TypeError, ValueError):
        return 0
    if v < 1:
        return 0
    entero = int(math.floor(v))
    return int(str(entero)[0])


def distribucion_primer_digito(importes) -> dict:
    """Cuenta el primer dígito (1..9) sobre una lista de importes >=1."""
    obs = {}
    for imp in importes:
        d = primer_digito(imp)
        if 1 <= d <= 9:
            obs[d] = obs.get(d, 0) + 1
    return obs


# ---------------------------------------------------------------------------
# Redondos (solo concentración por cuenta, nunca uno aislado)
# ---------------------------------------------------------------------------

def es_redondo(importe) -> bool:
    """True si el importe (>=100) es múltiplo exacto de 100."""
    try:
        v = float(importe)
    except (TypeError, ValueError):
        return False
    return v >= 100 and (round(v, 2) % 100 == 0)


def segmentos_redondos_anomalos(por_segmento: dict) -> list:
    """
    por_segmento = {clave: (n_redondos, n_total)}.
    Devuelve las cuentas con concentración anómala (ratio por encima del umbral y número
    mínimo de redondos). NUNCA marca un redondo aislado: exige concentración.
    """
    alertas = []
    for clave, (n_red, n_tot) in por_segmento.items():
        if n_tot <= 0:
            continue
        ratio = n_red / n_tot
        if n_red >= REDONDOS_MIN_EN_SEGMENTO and ratio >= REDONDOS_RATIO_ALERTA:
            alertas.append((clave, n_red, n_tot, round(ratio, 4)))
    alertas.sort(key=lambda x: x[3], reverse=True)
    return alertas


# ---------------------------------------------------------------------------
# Tercero fantasma (cuenta de tercero sin rastro documental)
# ---------------------------------------------------------------------------

def es_tercero_fantasma(cuenta, referencia_documento, hash_factura, tipo_operacion) -> bool:
    """
    True si una línea de cuenta de tercero (40/41/43/44) NO tiene rastro documental
    (referencia y hash vacíos) y NO es entrada de sistema.

    Nunca marca la cuenta madre '...0001' (una plantilla que no debe usarse nunca).
    Es INFORMATIVA: "sin rastro" es calidad de dato, no una acusación. Solo sube a
    candidato serio si se combina con otra señal (importe alto, tercero único).
    """
    c = str(cuenta) if cuenta is not None else ""
    if not (c.startswith("40") or c.startswith("41")
            or c.startswith("43") or c.startswith("44")):
        return False
    if c.endswith("0001"):                                   # cuenta madre, nunca
        return False
    if (tipo_operacion or "").upper() in TIPOS_SISTEMA:      # entradas de sistema
        return False
    sin_referencia = referencia_documento is None or str(referencia_documento).strip() == ""
    sin_hash = hash_factura is None or str(hash_factura).strip() == ""
    return sin_referencia and sin_hash


# ---------------------------------------------------------------------------
# Duplicados (la misma línea exacta repetida)
# ---------------------------------------------------------------------------

def agrupar_duplicados(lineas) -> list:
    """
    `lineas` = iterable de dicts con: `referencia_documento`, `cuenta`, `debe`, `haber`,
    `tipo_operacion`. Devuelve los grupos `(clave, n)` con n>1 que son DUPLICADO REAL:
    misma `(referencia, cuenta, debe, haber)` exacta repetida, excluyendo referencia
    nula y entradas de sistema.

    La clave separa debe y haber: el par factura (debe>0) más cobro (haber>0) toca la
    misma cuenta y referencia en LADOS OPUESTOS, así que da distinta clave y NO agrupa.
    Eso es una operación legítima, no un duplicado.
    """
    conteo = {}
    for ln in lineas:
        ref = ln.get("referencia_documento")
        if ref is None or str(ref).strip() == "":           # referencia nula: excluida
            continue
        if (ln.get("tipo_operacion") or "").upper() in TIPOS_SISTEMA:
            continue
        clave = (str(ref), str(ln.get("cuenta")),
                 round(float(ln.get("debe") or 0), 2),
                 round(float(ln.get("haber") or 0), 2))
        conteo[clave] = conteo.get(clave, 0) + 1
    return [(k, n) for k, n in conteo.items() if n > 1]


# ---------------------------------------------------------------------------
# Utilidad de fechas
# ---------------------------------------------------------------------------

def _a_fecha(x):
    """Normaliza a `date`. Acepta date/datetime o str ISO 'YYYY-MM-DD...'. None/'' -> None."""
    if x is None or x == "":
        return None
    if isinstance(x, datetime):
        return x.date()
    if isinstance(x, date):
        return x
    try:
        return datetime.strptime(str(x)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Fraccionamiento (structuring): partir un pago grande en varios parecidos
# ---------------------------------------------------------------------------

def detectar_fraccionamiento(lineas, ventana_dias=FRACC_VENTANA_DIAS, banda_pct=FRACC_BANDA_PCT,
                             min_n=FRACC_MIN_N, umbral_suma=FRACC_UMBRAL_SUMA) -> list:
    """
    Detecta FRACCIONAMIENTO: `min_n` o más líneas a la MISMA cuenta de tercero (40/41)
    en una ventana de `ventana_dias` días, con importes similares entre sí (mas o menos
    `banda_pct`) y suma del clúster por encima de `umbral_suma`. Es el hueco que el
    duplicado exacto no ve: partir 9.000 euros en 3 de 3.000 a tres referencias distintas
    (cuadran, tienen rastro, no son redondos), y aun así es sospechoso.

    `lineas` = iterable de dicts: `cuenta`, `fecha`, `importe`, `referencia_documento`,
    `tipo_operacion`. Control negativo incorporado: excluye cuenta madre '...0001',
    entradas de sistema y pagos recurrentes legítimos (referencia NOM-*/PAGNOM-*). Solo
    cuentas 40/41. Devuelve `(cuenta, n, suma, fecha_min, fecha_max)`, sin solapamiento.
    """
    por_cuenta = {}
    for ln in lineas:
        c = str(ln.get("cuenta") or "")
        if not (c.startswith("40") or c.startswith("41")):
            continue
        if c.endswith("0001"):                                   # cuenta madre, nunca
            continue
        if (ln.get("tipo_operacion") or "").upper() in TIPOS_SISTEMA:
            continue
        ref = str(ln.get("referencia_documento") or "")
        if ref.upper().startswith(REF_RECURRENTE):               # nóminas: legítimo
            continue
        f = _a_fecha(ln.get("fecha"))
        try:
            imp = float(ln.get("importe") or 0)
        except (TypeError, ValueError):
            continue
        if f is None or imp <= 0:
            continue
        por_cuenta.setdefault(c, []).append((f, imp))

    clusteres = []
    for c, items in por_cuenta.items():
        items.sort(key=lambda t: t[0])                            # por fecha
        usados = [False] * len(items)
        for i in range(len(items)):
            if usados[i]:
                continue
            f0, imp0 = items[i]
            lo, hi = imp0 * (1 - banda_pct), imp0 * (1 + banda_pct)
            miembros = []
            for j in range(i, len(items)):
                if usados[j]:
                    continue
                fj, impj = items[j]
                if (fj - f0).days > ventana_dias:
                    break
                if lo <= impj <= hi:
                    miembros.append(j)
            if len(miembros) >= min_n:
                suma = sum(items[j][1] for j in miembros)
                if suma >= umbral_suma:
                    for j in miembros:
                        usados[j] = True
                    fechas = [items[j][0] for j in miembros]
                    clusteres.append((c, len(miembros), round(suma, 2),
                                      min(fechas).isoformat(), max(fechas).isoformat()))
    clusteres.sort(key=lambda x: x[2], reverse=True)
    return clusteres


# ---------------------------------------------------------------------------
# Coherencia de las tres fechas (kiting/lapping temporal)
# ---------------------------------------------------------------------------

def incoherencias_fecha(fecha, fecha_vencimiento, fecha_cobro_pago, hoy=None) -> list:
    """
    Detecta INCOHERENCIAS entre las tres fechas de una línea. Un valor nulo NO se marca.
    Devuelve flags:
      'FECHA_FUTURA'                : fecha de asiento posterior a hoy (calidad de dato).
      'VENCIMIENTO_ANTES_DE_FECHA'  : vencimiento anterior a la fecha del asiento (imposible).
      'COBRO_ANTES_DE_FECHA'        : cobro/pago anterior a la fecha del asiento (imposible).
    Las dos últimas son accionables: un cobro no puede ocurrir antes de que exista el asiento.
    """
    f = _a_fecha(fecha)
    fv = _a_fecha(fecha_vencimiento)
    fc = _a_fecha(fecha_cobro_pago)
    h = _a_fecha(hoy) if hoy is not None else date.today()
    flags = []
    if f is not None and h is not None and f > h:
        flags.append("FECHA_FUTURA")
    if f is not None and fv is not None and fv < f:
        flags.append("VENCIMIENTO_ANTES_DE_FECHA")
    if f is not None and fc is not None and fc < f:
        flags.append("COBRO_ANTES_DE_FECHA")
    return flags


# ---------------------------------------------------------------------------
# Casi-duplicado (el pago repetido que evade el duplicado exacto)
# ---------------------------------------------------------------------------

def detectar_casi_duplicados(lineas, tol_abs=CASIDUP_TOL_ABS, ventana_dias=CASIDUP_VENTANA_DIAS) -> list:
    """
    `lineas` = iterable de dicts: `cuenta`, `fecha`, `importe` (el cargo>0),
    `referencia_documento`, `tipo_operacion`. Solo cuentas 40/41 (proveedor), no madre
    '...0001', no sistema. Agrupa por cuenta los cargos con importe a mas o menos `tol_abs`
    dentro de `ventana_dias`; reporta el clúster (n>=2) SALVO el caso que ya cubre el
    duplicado exacto (misma referencia no nula e importe idéntico).

    Devuelve `(cuenta, n, importe_medio, fecha_min, fecha_max, motivo)` con motivo en
    {IMPORTE_CASI, REF_DISTINTA, REF_NULA}. Capta el pago que se escapa por un céntimo,
    por referencia distinta o por referencia en blanco.
    """
    por_cuenta = {}
    for ln in lineas:
        c = str(ln.get("cuenta") or "")
        if not (c.startswith("40") or c.startswith("41")) or c.endswith("0001"):
            continue
        if (ln.get("tipo_operacion") or "").upper() in TIPOS_SISTEMA:
            continue
        f = _a_fecha(ln.get("fecha"))
        try:
            imp = float(ln.get("importe") or 0)
        except (TypeError, ValueError):
            continue
        if f is None or imp <= 0:
            continue
        ref = ln.get("referencia_documento")
        ref = None if (ref is None or str(ref).strip() == "") else str(ref)
        por_cuenta.setdefault(c, []).append((f, imp, ref))

    clusteres = []
    for c, items in por_cuenta.items():
        items.sort(key=lambda t: t[0])
        usados = [False] * len(items)
        for i in range(len(items)):
            if usados[i]:
                continue
            f0, imp0, _ = items[i]
            miembros = [i]
            for j in range(i + 1, len(items)):
                if usados[j]:
                    continue
                fj, impj, _ = items[j]
                if (fj - f0).days > ventana_dias:
                    break
                if abs(impj - imp0) <= tol_abs:
                    miembros.append(j)
            if len(miembros) < 2:
                continue
            refs = [items[k][2] for k in miembros]
            imps = [items[k][1] for k in miembros]
            hay_nula = any(r is None for r in refs)
            refs_nn = [r for r in refs if r is not None]
            importe_identico = (max(imps) - min(imps)) < 1e-9
            todas_misma_ref = len(refs_nn) == len(refs) and len(set(refs_nn)) == 1
            # Caso exacto del duplicado (misma ref no nula e importe idéntico): no se repite aquí.
            if importe_identico and todas_misma_ref:
                continue
            motivo = ("REF_NULA" if hay_nula
                      else "IMPORTE_CASI" if not importe_identico
                      else "REF_DISTINTA")
            for k in miembros:
                usados[k] = True
            fechas = [items[k][0] for k in miembros]
            clusteres.append((c, len(miembros), round(sum(imps) / len(imps), 2),
                              min(fechas).isoformat(), max(fechas).isoformat(), motivo))
    clusteres.sort(key=lambda x: x[2], reverse=True)
    return clusteres


# ---------------------------------------------------------------------------
# Huecos de secuencia de numeración (informativo, calidad de dato)
# ---------------------------------------------------------------------------

def huecos_secuencia(numeros) -> dict:
    """
    Cuenta los saltos en la numeración de asientos. `numeros` = iterable de enteros.
    Devuelve {min, max, distintos, huecos}. Es INFORMATIVO: un hueco puede ser un
    asiento anulado legítimo o un salto de diseño, no necesariamente algo borrado.
    Solo cobra valor sobre una numeración que se garantiza contigua (dato real).
    """
    vistos = set()
    for x in numeros:
        try:
            vistos.add(int(x))
        except (TypeError, ValueError):
            continue
    if not vistos:
        return {"min": None, "max": None, "distintos": 0, "huecos": 0}
    mn, mx = min(vistos), max(vistos)
    huecos = (mx - mn + 1) - len(vistos)
    return {"min": mn, "max": mx, "distintos": len(vistos), "huecos": huecos}
