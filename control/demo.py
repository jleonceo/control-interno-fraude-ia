# -*- coding: utf-8 -*-
"""
demo.py -- Pasa la batería forense sobre el libro sintético y comprueba dos cosas:
que caza el fraude sembrado, y que NO marca lo legítimo (los controles negativos).

La demo es a la vez ejemplo y prueba: al final dice si todo cuadra contra la "verdad"
conocida del generador. Si algo no cuadra, sale con código de error.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from control import motor
from datos_ejemplo.generar_libro import generar_libro

HOY_DEMO = "2026-12-31"   # posterior a todas las fechas del libro: aísla la incoherencia sembrada


def _titulo(t):
    print("\n" + "=" * 74)
    print(t)
    print("=" * 74)


def _importe(ln):
    return max(float(ln["debe"] or 0), float(ln["haber"] or 0))


def ejecutar():
    lineas, gt, benford = generar_libro()
    fallos = []

    def check(condicion, etiqueta):
        marca = "OK  " if condicion else "FALLO"
        print(f"  [{marca}] {etiqueta}")
        if not condicion:
            fallos.append(etiqueta)

    _titulo("LIBRO SINTÉTICO")
    print(f"  {len(lineas)} líneas de asiento. Semilla fija, sin datos reales.")
    print(f"  Fraude sembrado: {', '.join(gt['fraude'].keys())}")
    print(f"  Controles negativos: {', '.join(gt['controles_negativos'].keys())}")

    # -- Duplicados ---------------------------------------------------------------
    _titulo("DUPLICADOS (misma línea exacta repetida)")
    dups = motor.agrupar_duplicados(lineas)
    refs_dup = {k[0] for k, _ in dups}
    ref_sembrada = gt["fraude"]["duplicado"]["ref"]
    print(f"  Grupos duplicados encontrados: {len(dups)} -> {sorted(refs_dup)}")
    check(ref_sembrada in refs_dup, f"caza el duplicado sembrado ({ref_sembrada})")
    check("FAC-V000" not in refs_dup and all(not r.startswith("FAC-V") for r in refs_dup),
          "control negativo: factura+cobro (lados opuestos) NO se marca como duplicado")

    # -- Fraccionamiento ----------------------------------------------------------
    _titulo("FRACCIONAMIENTO (pago grande partido en varios parecidos)")
    lin_imp = [{**ln, "importe": _importe(ln)} for ln in lineas]
    fracc = motor.detectar_fraccionamiento(lin_imp)
    ctas_fracc = {k[0] for k in fracc}
    cta_fracc = gt["fraude"]["fraccionamiento"]["cuenta"]
    print(f"  Clústeres: {len(fracc)} -> {[(k[0], k[1], k[2]) for k in fracc]}")
    check(cta_fracc in ctas_fracc, f"caza el fraccionamiento sembrado ({cta_fracc}, 3x3.000)")
    check(gt["controles_negativos"]["nomina_recurrente"]["cuenta"] not in ctas_fracc,
          "control negativo: nóminas recurrentes NO son fraccionamiento")

    # -- Casi-duplicado -----------------------------------------------------------
    _titulo("CASI-DUPLICADO (el pago repetido que se escapa por un céntimo)")
    casi = motor.detectar_casi_duplicados(lin_imp)
    ctas_casi = {k[0] for k in casi}
    cta_casi = gt["fraude"]["casi_duplicado"]["cuenta"]
    print(f"  Clústeres: {len(casi)} -> {[(k[0], k[2], k[5]) for k in casi]}")
    check(cta_casi in ctas_casi, f"caza el casi-duplicado sembrado ({cta_casi}, 742,30 vs 742,31)")

    # -- Tercero fantasma ---------------------------------------------------------
    _titulo("TERCERO FANTASMA (cuenta de tercero sin rastro documental)")
    fantasma = sorted({ln["cuenta"] for ln in lineas
                       if motor.es_tercero_fantasma(ln["cuenta"], ln["referencia_documento"],
                                                     ln["hash_factura"], ln["tipo_operacion"])})
    cta_fant = gt["fraude"]["fantasma"]["cuenta"]
    print(f"  Cuentas señaladas (informativo): {fantasma}")
    check(cta_fant in fantasma, f"señala la cuenta fantasma sembrada ({cta_fant})")
    check(not any(ln["tipo_operacion"] == "APERTURA" and ln["cuenta"] in fantasma
                  for ln in lineas),
          "control negativo: asientos de sistema (APERTURA) NO se marcan como fantasma")

    # -- Coherencia de fechas -----------------------------------------------------
    _titulo("COHERENCIA DE FECHAS (cobro o vencimiento imposibles en el tiempo)")
    accionables = []
    for ln in lineas:
        flags = motor.incoherencias_fecha(ln["fecha"], ln["fecha_vencimiento"],
                                           ln["fecha_cobro_pago"], hoy=HOY_DEMO)
        acc = [f for f in flags if f != "FECHA_FUTURA"]
        if acc:
            accionables.append((ln["referencia_documento"], acc))
    flag_esperado = gt["fraude"]["incoherencia_fecha"]["flag"]
    print(f"  Incoherencias accionables: {accionables}")
    check(any(flag_esperado in acc for _, acc in accionables),
          f"caza la incoherencia sembrada ({flag_esperado})")

    # -- Redondos -----------------------------------------------------------------
    _titulo("REDONDOS (concentración anómala por cuenta, nunca uno aislado)")
    por_cuenta = {}
    for ln in lineas:
        imp = _importe(ln)
        if imp < 100:
            continue
        cta = str(ln["cuenta"])
        if cta.startswith(motor.CUENTAS_REDONDAS_POR_NATURALEZA):
            continue
        nr, nt = por_cuenta.get(cta, (0, 0))
        por_cuenta[cta] = (nr + (1 if motor.es_redondo(imp) else 0), nt + 1)
    alertas = motor.segmentos_redondos_anomalos(por_cuenta)
    ctas_red = {a[0] for a in alertas}
    cta_red = gt["fraude"]["redondos"]["cuenta"]
    print(f"  Cuentas con concentración de redondos: {[(a[0], a[1], a[2]) for a in alertas]}")
    check(cta_red in ctas_red, f"caza la concentración de redondos sembrada ({cta_red})")
    check(gt["controles_negativos"]["deuda_redonda"]["cuenta"] not in ctas_red,
          "control negativo: redondos en cuenta de deuda (por naturaleza) NO se marcan")

    # -- Huecos de secuencia ------------------------------------------------------
    _titulo("HUECOS DE SECUENCIA (informativo, calidad de dato)")
    h = motor.huecos_secuencia(ln["num_asiento"] for ln in lineas)
    print(f"  num_asiento {h['min']}..{h['max']}, {h['distintos']} distintos -> {h['huecos']} huecos.")
    check(h["huecos"] > 0, "detecta huecos en la numeración (se listan, no se acusan)")

    # -- Benford ------------------------------------------------------------------
    _titulo("BENFORD (primer dígito: curva limpia frente a cifras manipuladas)")
    obs_limpio = motor.distribucion_primer_digito(benford["limpio"])
    obs_manip = motor.distribucion_primer_digito(benford["manipulado"])
    n_l, n_m = sum(obs_limpio.values()), sum(obs_manip.values())
    chi_l = motor.benford_chi2(obs_limpio, n_l)
    chi_m = motor.benford_chi2(obs_manip, n_m)
    print(f"  Muestra limpia:      chi2 = {chi_l:8.1f}  (sigue la curva)")
    print(f"  Muestra manipulada:  chi2 = {chi_m:8.1f}  (se aleja de la curva)")
    check(chi_m > chi_l * 3, "distingue la muestra manipulada de la limpia (chi2 mucho mayor)")
    gate = motor.decision_gate_benford(len(benford["limpio"]))
    print(f"  Gate de tamaño sobre {len(benford['limpio'])} importes: {gate} "
          f"(por debajo de {motor.BENFORD_MIN_REGISTROS} no se considera fiable).")

    # -- Veredicto ----------------------------------------------------------------
    _titulo("VEREDICTO DE LA DEMO")
    if fallos:
        print(f"  {len(fallos)} comprobación(es) FALLAN:")
        for f in fallos:
            print(f"    - {f}")
        print("\n  La batería NO cuadra contra la verdad conocida del libro.")
        return False
    print("  TODO VERDE: caza el fraude sembrado y deja limpios los controles negativos.")
    print("  Recordatorio: cada prueba PROPONE candidatos a revisión humana, no acusa.")
    return True


if __name__ == "__main__":
    sys.exit(0 if ejecutar() else 1)
