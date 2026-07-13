# -*- coding: utf-8 -*-
"""
probar_todo.py -- Ejecuta todo de una vez, sin instalar nada.

  1) Autotest de las funciones puras (control positivo y negativo de cada prueba).
  2) Genera el libro sintético y lo escribe a CSV.
  3) Pasa la batería forense sobre ese libro y comprueba el resultado.

Sale con código 0 si todo va verde, 1 si algo falla. Solo Python estándar.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from control import motor
from control import demo
from datos_ejemplo.generar_libro import generar_libro, escribir_csv


def autotest_funciones_puras():
    """Valida la lógica con entradas conocidas, sin datos ni base de datos."""
    print("=" * 74)
    print("AUTOTEST DE FUNCIONES PURAS (sin datos, control positivo y negativo)")
    print("=" * 74)
    ok = True

    def check(cond, etiqueta):
        nonlocal ok
        print(f"  [{'OK  ' if cond else 'FALLO'}] {etiqueta}")
        ok = ok and cond

    # Benford: la curva esperada suma 1; chi2 = 0 en la distribución perfecta y sube al sesgar.
    check(abs(sum(motor.BENFORD_1D.values()) - 1.0) < 1e-9, "la curva de Benford suma 1")
    n = 100000
    perfecto = {d: round(motor.BENFORD_1D[d] * n) for d in range(1, 10)}
    check(motor.benford_chi2(perfecto, sum(perfecto.values())) < 1.0,
          "chi2 de una distribución perfecta es casi 0")
    check(motor.benford_chi2({1: n}, n) > 1000,
          "chi2 de una distribución sesgada (todo dígito 1) es alto")

    # Gate de tamaño: 80 manual no aplica; 6000 sí.
    check(motor.decision_gate_benford(80) == "NO_APLICA", "gate Benford con 80 líneas: NO_APLICA")
    check(motor.decision_gate_benford(6000) == "APLICA", "gate Benford con 6000 líneas: APLICA")

    # Redondos: 1000 y 200 sí; 199,80 y 50 no. Concentración 8/10 alerta; 2/100 y aislado no.
    check(motor.es_redondo(1000) and motor.es_redondo(200), "1000 y 200 son redondos")
    check(not motor.es_redondo(199.80) and not motor.es_redondo(50), "199,80 y 50 no son redondos")
    alertas = motor.segmentos_redondos_anomalos({"A": (8, 10), "B": (2, 100), "C": (1, 1)})
    claves = {a[0] for a in alertas}
    check("A" in claves and "B" not in claves and "C" not in claves,
          "concentración 8/10 alerta; 2/100 y el aislado 1/1 no")

    # Fantasma: tercero sin rastro sí; con referencia, madre o sistema no; cuenta de ingreso no.
    check(motor.es_tercero_fantasma("41000005", None, None, "COMPRA"),
          "tercero 41 sin ref ni hash: fantasma")
    check(not motor.es_tercero_fantasma("41000005", "FAC-1", None, "COMPRA"),
          "con referencia: NO fantasma")
    check(not motor.es_tercero_fantasma("41000001", None, None, "COMPRA"),
          "cuenta madre ...0001: nunca fantasma")
    check(not motor.es_tercero_fantasma("41000005", None, None, "CIERRE"),
          "entrada de sistema (CIERRE): NO fantasma")
    check(not motor.es_tercero_fantasma("70000002", None, None, "VENTA"),
          "cuenta de ingreso (70): no es cuenta de tercero")

    # Duplicados: línea exacta repetida sí; factura+cobro (lados opuestos) no; ref nula no.
    dup = motor.agrupar_duplicados([
        {"referencia_documento": "FAC-9", "cuenta": "40000002", "debe": 0, "haber": 100, "tipo_operacion": "COMPRA"},
        {"referencia_documento": "FAC-9", "cuenta": "40000002", "debe": 0, "haber": 100, "tipo_operacion": "COMPRA"},
        {"referencia_documento": "FAC-7", "cuenta": "43000002", "debe": 100, "haber": 0, "tipo_operacion": "VENTA"},
        {"referencia_documento": "FAC-7", "cuenta": "43000002", "debe": 0, "haber": 100, "tipo_operacion": "COBRO"},
        {"referencia_documento": None, "cuenta": "47500002", "debe": 0, "haber": 41497.27, "tipo_operacion": "FISCAL"},
        {"referencia_documento": None, "cuenta": "47500002", "debe": 0, "haber": 41497.27, "tipo_operacion": "FISCAL"},
    ])
    claves_dup = {k for k, _ in dup}
    check(("FAC-9", "40000002", 0.0, 100.0) in claves_dup, "línea exacta repetida: duplicado")
    check(not any(k[0] == "FAC-7" for k in claves_dup), "factura+cobro (lados opuestos): NO duplicado")
    check(len(dup) == 1, "la referencia nula (sistema) se excluye del duplicado")

    # Fraccionamiento: 3x3.000 misma cuenta en 5 días sí; nóminas no; disperso >7 días no.
    fracc = motor.detectar_fraccionamiento([
        {"cuenta": "40000009", "fecha": "2026-03-01", "importe": 3000, "referencia_documento": "FAC-A", "tipo_operacion": "COMPRA"},
        {"cuenta": "40000009", "fecha": "2026-03-03", "importe": 3000, "referencia_documento": "FAC-B", "tipo_operacion": "COMPRA"},
        {"cuenta": "40000009", "fecha": "2026-03-05", "importe": 3000, "referencia_documento": "FAC-C", "tipo_operacion": "COMPRA"},
    ])
    check(any(k[0] == "40000009" for k in fracc), "3x3.000 en 5 días: fraccionamiento")
    check(not motor.detectar_fraccionamiento([
        {"cuenta": "41000010", "fecha": "2026-03-01", "importe": 2000, "referencia_documento": "NOM-1", "tipo_operacion": "NOMINA"},
        {"cuenta": "41000010", "fecha": "2026-03-02", "importe": 2000, "referencia_documento": "NOM-2", "tipo_operacion": "NOMINA"},
        {"cuenta": "41000010", "fecha": "2026-03-03", "importe": 2000, "referencia_documento": "NOM-3", "tipo_operacion": "NOMINA"},
    ]), "nóminas recurrentes NOM-*: NO fraccionamiento")
    check(not motor.detectar_fraccionamiento([
        {"cuenta": "40000006", "fecha": "2026-01-01", "importe": 3000, "referencia_documento": "F1", "tipo_operacion": "COMPRA"},
        {"cuenta": "40000006", "fecha": "2026-02-01", "importe": 3000, "referencia_documento": "F2", "tipo_operacion": "COMPRA"},
        {"cuenta": "40000006", "fecha": "2026-03-01", "importe": 3000, "referencia_documento": "F3", "tipo_operacion": "COMPRA"},
    ]), "importes dispersos en más de 7 días: NO fraccionamiento")

    # Coherencia de fechas: vencimiento<fecha sí; coherentes no; futura sí; nulos no.
    check("VENCIMIENTO_ANTES_DE_FECHA" in motor.incoherencias_fecha("2026-03-10", "2026-03-01", None, hoy="2026-06-30"),
          "vencimiento anterior a la fecha del asiento: incoherencia")
    check(not motor.incoherencias_fecha("2026-03-10", "2026-04-10", "2026-03-17", hoy="2026-06-30"),
          "fechas coherentes: sin incoherencia")
    check("FECHA_FUTURA" in motor.incoherencias_fecha("2026-07-15", None, None, hoy="2026-06-30"),
          "fecha de asiento futura: se marca (calidad de dato)")
    check(not motor.incoherencias_fecha("2026-03-10", None, None, hoy="2026-06-30"),
          "fecha presente y nulos: sin incoherencia")

    # Casi-duplicado: capta céntimo, ref distinta y ref nula; no re-reporta el duplicado exacto.
    cd = motor.detectar_casi_duplicados([
        {"cuenta": "40000011", "fecha": "2026-03-01", "importe": 500.00, "referencia_documento": "F1", "tipo_operacion": "COMPRA"},
        {"cuenta": "40000011", "fecha": "2026-03-02", "importe": 500.01, "referencia_documento": "F1", "tipo_operacion": "COMPRA"}])
    check(any(k[5] == "IMPORTE_CASI" for k in cd), "diferencia de un céntimo: casi-duplicado")
    check(not motor.detectar_casi_duplicados([
        {"cuenta": "40000014", "fecha": "2026-03-01", "importe": 700.0, "referencia_documento": "F9", "tipo_operacion": "COMPRA"},
        {"cuenta": "40000014", "fecha": "2026-03-02", "importe": 700.0, "referencia_documento": "F9", "tipo_operacion": "COMPRA"}]),
          "el duplicado exacto (misma ref, mismo importe) no se re-reporta aquí")

    # Huecos: secuencia con salto detecta el hueco; contigua no.
    check(motor.huecos_secuencia([1, 2, 5])["huecos"] == 2, "secuencia 1,2,5: 2 huecos")
    check(motor.huecos_secuencia([1, 2, 3])["huecos"] == 0, "secuencia contigua: 0 huecos")

    print(f"\n  {'AUTOTEST VERDE' if ok else 'AUTOTEST CON FALLOS'}")
    return ok


def main():
    ok1 = autotest_funciones_puras()

    print("\n" + "=" * 74)
    print("GENERAR LIBRO SINTÉTICO")
    print("=" * 74)
    lineas, _, _ = generar_libro()
    ruta = escribir_csv(lineas)
    print(f"  Escrito: {ruta} ({len(lineas)} líneas).")

    ok2 = demo.ejecutar()

    print("\n" + "=" * 74)
    print("RESULTADO GLOBAL")
    print("=" * 74)
    if ok1 and ok2:
        print("  TODO VERDE.")
        return 0
    print("  HAY FALLOS.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
