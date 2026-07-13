# -*- coding: utf-8 -*-
"""
generar_libro.py -- Libro de asientos SINTÉTICO con fraude sembrado y controles negativos.

No hay ningún dato real ni personal. Todo se genera con una semilla fija, así que el
libro es idéntico en cada ejecución y la "verdad" de lo que hay dentro se conoce de
antemano (ground truth). Sobre ese libro conocido se puede comprobar que cada prueba
forense caza lo que debe y NO marca lo legítimo.

El libro trae, a propósito:
  Fraude sembrado (lo que las pruebas DEBEN cazar):
    - un duplicado exacto (misma referencia, cuenta, debe y haber, repetido);
    - un fraccionamiento (un pago grande partido en tres parecidos al mismo proveedor);
    - un casi-duplicado (el mismo pago repetido con un céntimo de diferencia);
    - una cuenta de tercero fantasma (mueve dinero sin ningún rastro documental);
    - una incoherencia de fechas (un cobro anterior a la fecha del propio asiento);
    - una concentración anómala de importes redondos en una cuenta de gasto;
    - huecos en la numeración de asientos.
  Controles negativos (lo que las pruebas NO deben marcar):
    - facturas de venta con su cobro (misma referencia, lados opuestos): legítimo;
    - nóminas recurrentes de importe parecido (no es fraccionamiento);
    - importes redondos en una cuenta de deuda (redondos por naturaleza);
    - asientos de sistema sin documento (apertura/cierre).

Además genera dos muestras de importes para la prueba de Benford: una que sigue la
curva y otra manipulada, para ver la diferencia sin depender de datos reales.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEMILLA = 20260713
AQUI = Path(__file__).parent
CSV_LIBRO = AQUI / "libro_sintetico.csv"

CAMPOS = [
    "num_asiento", "fecha", "cuenta", "debe", "haber",
    "referencia_documento", "hash_factura", "tipo_operacion",
    "fecha_vencimiento", "fecha_cobro_pago", "origen",
]

_BASE = date(2026, 1, 8)


def _f(dias):
    """Fecha base más `dias` días, en ISO."""
    return (_BASE + timedelta(days=dias)).isoformat()


def _linea(num, fecha, cuenta, debe, haber, ref, hsh, tipo,
           venc=None, cobro=None, origen="MANUAL"):
    return {
        "num_asiento": num, "fecha": fecha, "cuenta": cuenta,
        "debe": round(float(debe), 2), "haber": round(float(haber), 2),
        "referencia_documento": ref, "hash_factura": hsh,
        "tipo_operacion": tipo, "fecha_vencimiento": venc,
        "fecha_cobro_pago": cobro, "origen": origen,
    }


def generar_libro():
    """
    Devuelve (lineas, ground_truth, benford). `lineas` es la lista de asientos;
    `ground_truth` dice qué se sembró y qué es control negativo; `benford` trae dos
    muestras de importes (limpia y manipulada) para la prueba de Benford.
    """
    rnd = random.Random(SEMILLA)
    lineas = []
    num = 1000  # numeración de asientos; se dejan huecos a propósito más abajo

    # -- Actividad legítima de compras: importes variados, no redondos, con rastro ------
    proveedores = ["40000002", "40000003", "40000004", "40000006", "40000007"]
    for i in range(60):
        cta = rnd.choice(proveedores)
        # Importe log-uniforme: primer dígito sigue aproximadamente a Benford.
        imp = round(10 ** rnd.uniform(2.0, 4.0) + rnd.uniform(0.01, 0.99), 2)
        d = _f(rnd.randint(0, 170))
        num += rnd.randint(1, 3)                       # avanza dejando huecos naturales
        lineas.append(_linea(num, d, cta, 0, imp, f"FAC-C{i:03d}",
                             f"h{rnd.getrandbits(48):012x}", "COMPRA",
                             venc=_f(rnd.randint(171, 210))))

    # -- Control negativo 1: factura de venta + su cobro (misma ref, lados opuestos) ----
    # NO es duplicado: debe y haber caen en lados opuestos de la misma cuenta/referencia.
    for i in range(12):
        cta = "43000002"
        imp = round(rnd.uniform(300, 5000), 2)
        d = _f(rnd.randint(0, 150))
        ref = f"FAC-V{i:03d}"
        num += rnd.randint(1, 2)
        lineas.append(_linea(num, d, cta, imp, 0, ref, f"h{rnd.getrandbits(48):012x}",
                             "VENTA", venc=_f(rnd.randint(151, 180))))
        num += rnd.randint(1, 2)
        lineas.append(_linea(num, _f(rnd.randint(151, 175)), cta, 0, imp, ref,
                             f"h{rnd.getrandbits(48):012x}", "COBRO"))

    # -- Control negativo 2: nóminas recurrentes de importe parecido (no es fraccionar) -
    for i in range(4):
        num += 1
        lineas.append(_linea(num, _f(30 * i + 5), "41000010",
                             0, round(1800 + rnd.uniform(-20, 20), 2),
                             f"NOM-{i:03d}", None, "NOMINA"))

    # -- Control negativo 3: importes redondos en cuenta de DEUDA (redondos naturales) --
    for i in range(6):
        num += 1
        lineas.append(_linea(num, _f(20 * i + 3), "17000001",
                             0, 1000.00, f"PREST-{i:03d}", None, "MANUAL"))

    # -- Control negativo 4: asientos de sistema sin documento (apertura/cierre) --------
    for cta in ("41000002", "43000002", "47700001"):
        num += 1
        lineas.append(_linea(num, _f(0), cta, 0, round(rnd.uniform(500, 9000), 2),
                             None, None, "APERTURA", origen="SISTEMA"))

    # ------------------------------------------------------------------------------
    # FRAUDE SEMBRADO
    # ------------------------------------------------------------------------------

    # F1 - Duplicado exacto: misma (ref, cuenta, debe, haber) repetida en dos líneas.
    dup_ref, dup_cta, dup_imp = "FAC-DUP-91", "40000002", 1250.00
    for _ in range(2):
        num += 1
        lineas.append(_linea(num, _f(88), dup_cta, 0, dup_imp, dup_ref,
                             "hdupdupdup01", "COMPRA"))

    # F2 - Fraccionamiento: 9.000 partido en 3 de 3.000 al mismo proveedor en 5 días.
    fracc_cta = "40000009"
    for k, dd in enumerate((100, 102, 105)):
        num += 1
        lineas.append(_linea(num, _f(dd), fracc_cta, 0, 3000.00,
                             f"FAC-FR{k}", f"hfr{k:09d}", "COMPRA"))

    # F3 - Casi-duplicado: el mismo pago repetido con un céntimo de diferencia.
    casidup_cta = "40000011"
    num += 1
    lineas.append(_linea(num, _f(120), casidup_cta, 0, 742.30, "FAC-K1",
                         "hk1k1k1k101", "COMPRA"))
    num += 1
    lineas.append(_linea(num, _f(121), casidup_cta, 0, 742.31, "FAC-K2",
                         "hk2k2k2k201", "COMPRA"))

    # F4 - Tercero fantasma: cuenta de tercero que mueve dinero sin ref ni hash.
    fantasma_cta = "41000005"
    for dd in (60, 92, 130):
        num += 1
        lineas.append(_linea(num, _f(dd), fantasma_cta,
                             0, round(rnd.uniform(2000, 9000), 2),
                             None, None, "COMPRA"))

    # F5 - Incoherencia de fechas: un cobro registrado ANTES de la fecha del asiento.
    incoh_ref = "FAC-INC-01"
    num += 1
    lineas.append(_linea(num, _f(140), "43000002", 2400.00, 0, incoh_ref,
                         "hinc0000001", "VENTA",
                         venc=_f(170), cobro=_f(133)))   # cobro (día 133) antes de fecha (día 140)

    # F6 - Concentración de redondos en una cuenta de gasto (6 redondos, ratio alto).
    redondos_cta = "62900099"
    for i in range(6):
        num += 1
        lineas.append(_linea(num, _f(40 + i * 3), redondos_cta,
                             round(rnd.choice([500, 1000, 1500, 2000]), 2), 0,
                             f"GAS-{i:03d}", f"hg{i:010d}", "GASTO"))
    # y una línea no redonda en la misma cuenta, para que el ratio sea realista, no 100%.
    num += 1
    lineas.append(_linea(num, _f(60), redondos_cta, 733.19, 0, "GAS-777",
                         "hg7777777777", "GASTO"))

    # F7 - Hueco de secuencia grande y deliberado (un bloque de numeración que falta).
    num += 50
    lineas.append(_linea(num, _f(160), "40000003", 0, 421.55, "FAC-Z1",
                         "hz1z1z1z101", "COMPRA"))

    lineas.sort(key=lambda x: x["num_asiento"])

    # ------------------------------------------------------------------------------
    # Muestras para Benford (importes sueltos, no asientos)
    # ------------------------------------------------------------------------------
    # Limpia: log-uniforme, el primer dígito sigue a Benford de forma natural.
    benford_limpio = [round(10 ** rnd.uniform(1.0, 5.0), 2) for _ in range(4000)]
    # Manipulada: la mitad de los importes forzados a empezar por 4 y 5 (dígitos raros
    # en Benford), como haría quien inventa cifras alrededor de un umbral de aprobación.
    benford_manipulado = list(benford_limpio)
    for i in range(0, len(benford_manipulado), 2):
        d = rnd.choice([4, 5])
        benford_manipulado[i] = round(d * 1000 + rnd.uniform(0, 999), 2)

    ground_truth = {
        "fraude": {
            "duplicado": {"ref": dup_ref, "cuenta": dup_cta, "importe": dup_imp},
            "fraccionamiento": {"cuenta": fracc_cta, "n": 3, "suma": 9000.00},
            "casi_duplicado": {"cuenta": casidup_cta, "motivo": "IMPORTE_CASI"},
            "fantasma": {"cuenta": fantasma_cta, "n_lineas": 3},
            "incoherencia_fecha": {"ref": incoh_ref, "flag": "COBRO_ANTES_DE_FECHA"},
            "redondos": {"cuenta": redondos_cta},
            "huecos": {"hay": True},
        },
        "controles_negativos": {
            "factura_cobro": {"cuenta": "43000002", "no_es": "duplicado"},
            "nomina_recurrente": {"cuenta": "41000010", "no_es": "fraccionamiento"},
            "deuda_redonda": {"cuenta": "17000001", "no_es": "redondos"},
            "sistema_sin_doc": {"tipo": "APERTURA", "no_es": "fantasma"},
        },
    }
    benford = {"limpio": benford_limpio, "manipulado": benford_manipulado}
    return lineas, ground_truth, benford


def escribir_csv(lineas, ruta=CSV_LIBRO):
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS)
        w.writeheader()
        for ln in lineas:
            w.writerow(ln)
    return ruta


if __name__ == "__main__":
    lineas, gt, _ = generar_libro()
    ruta = escribir_csv(lineas)
    print(f"Libro sintético escrito: {ruta} ({len(lineas)} líneas)")
    print(f"Fraude sembrado: {list(gt['fraude'].keys())}")
    print(f"Controles negativos: {list(gt['controles_negativos'].keys())}")
