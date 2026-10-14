English version: [README.en.md](README.en.md)

# Detección de fraude en el libro diario

Ocho pruebas de auditoría sobre un libro de asientos contables que señalan las líneas que conviene revisar:
duplicados, pagos partidos para no pasar por la firma del director, proveedores sin documentos, fechas
imposibles y la ley de Benford, entre otras.

**Resultado:** sobre un libro de ejemplo con 116 líneas, las pruebas encuentran las siete anomalías plantadas y
no marcan ninguno de los cuatro casos legítimos que se parecen a un fraude, como una factura con su cobro.

```bash
python probar_todo.py
```

Python estándar, sin nada que instalar, sin base de datos y sin red. Las mismas pruebas se ejecutan en GitHub
con dos versiones de Python.

## El problema de partida

Si las compras de más de 3.000 € las firma el director, quien quiera evitarlo puede pedir tres facturas de
3.000 € en lugar de una de 9.000 €. Cada factura, mirada sola, es correcta. El fraude solo se ve al mirar las
tres juntas, y en un libro de miles de líneas nadie lo hace a mano. Estas pruebas miran el libro entero y
proponen candidatos. Decidir si cada uno es un error, un descuido o un fraude le corresponde a una persona con
la documentación delante.

## Las ocho pruebas

| Prueba | Qué busca | Uso con datos reales |
|---|---|---|
| Duplicados | La misma línea repetida: referencia, cuenta, debe y haber | Para actuar |
| Fraccionamiento | Importes parecidos al mismo proveedor en pocos días | Para actuar |
| Casi duplicados | El mismo pago repetido con un céntimo o una referencia de diferencia | Para actuar |
| Coherencia de fechas | Un cobro o un vencimiento anterior a la fecha del asiento | Para actuar |
| Ley de Benford | La primera cifra de los importes se aparta de su reparto natural | Para actuar, con más de 5.000 importes |
| Importes redondos | Demasiados importes redondos en una misma cuenta | Señal de apoyo |
| Proveedor sin documentos | Una cuenta de tercero que mueve dinero sin factura ni referencia | Informativa, calidad del dato |
| Huecos de numeración | Saltos en la numeración de los asientos | Informativa, calidad del dato |

Cada prueba tiene además sus controles negativos: casos normales que no debe marcar. Una factura de venta y su
cobro tocan la misma cuenta con la misma referencia y no son un duplicado. Unas nóminas de importe parecido
cada mes tampoco son un pago partido.

## Lo que sale

- **Fraccionamiento:** la cuenta 40000009, con tres cargos de 3.000 € en cinco días, 9.000 € en total.
- **Duplicado:** la factura `FAC-DUP-91`.
- **Casi duplicado:** la cuenta 40000011, con dos pagos de 742,30 € y 742,31 €.
- **Proveedor sin documentos:** la cuenta 41000005.
- **Fecha imposible:** la factura `FAC-INC-01`, cobrada antes de la fecha de su asiento.
- **Importes redondos:** la cuenta 62900099, con 6 redondos en 7 líneas.
- **Benford:** separa una muestra manipulada de una limpia, con un chi cuadrado de 4.724,5 frente a 3,9.

## Límites

- Los datos son sintéticos y las anomalías se plantaron sabiendo qué buscan las pruebas. Demuestra que el
  cálculo funciona, no cuántos fraudes encontraría en una contabilidad real.
- Benford necesita más de 5.000 importes para ser fiable. Las muestras de ejemplo tienen 4.000, y el propio
  programa responde que la prueba no aplica. En una empresa pequeña casi nunca hay volumen suficiente.
- El generador salta números de asiento al azar, así que salen 112 huecos en 116 asientos. Sobre estos datos esa
  prueba no mide nada; solo tiene sentido en un libro con numeración correlativa garantizada.
- Los tres cargos de 3.000 € aparecen a la vez como pago partido y como casi duplicado. Se dejan así para no
  fingir una precisión que no hay.
- Un proveedor sin documentos suele ser un apunte antiguo mal archivado o una migración, no un fraude; por eso
  esa prueba es informativa. [caso_real.md](caso_real.md) explica el criterio de cada prueba.
- Del marco COSO de control interno, solo las actividades de control están programadas. Los otros cuatro
  componentes quedan como contexto.

## Datos

Todo es sintético y sale igual en cada ejecución, con la semilla 20260713. No hay datos reales ni personales, y
el programa solo lee: no escribe en ninguna base de datos.

## Repositorios relacionados

- [analisis-contable](https://github.com/jleonceo/analisis-contable): cuenta de resultados y tesorería de 2024
  con pandas, comprobadas por un segundo camino.
- [tesoreria-forecast-ia](https://github.com/jleonceo/tesoreria-forecast-ia): previsión de caja medida contra el
  pasado, ratios de liquidez y antigüedad de saldos.
- [accounting-agent-swarm](https://github.com/jleonceo/accounting-agent-swarm): agentes de IA que registran
  asientos contables con controles en cada paso.

---

*Parte del portfolio de [Juan Luis León](https://github.com/jleonceo) · [juanluisleon.vercel.app](https://juanluisleon.vercel.app) · Licencia [MIT](LICENSE)*
