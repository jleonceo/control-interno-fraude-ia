# control-interno-fraude-ia

**Encontrar el fraude escondido entre miles de apuntes contables usando solo aritmética.**
**Finding the fraud hidden among thousands of accounting entries using arithmetic alone.**

Sin dependencias (solo Python estándar), sin base de datos, sin IA, sin red.
No dependencies (standard Python only), no database, no AI, no network.

[Español](#español) · [English](#english)

---

## Español

### El problema

Imagina una empresa con una regla que cualquiera entiende: las compras por encima de tres mil euros las firma el director, y por debajo basta con la firma del responsable del área. La regla existe para que nadie mueva sumas gordas sin un segundo par de ojos encima.

Llega el responsable de compras, que encarga una reforma de nueve mil euros y pide al proveedor tres facturas de tres mil, con números distintos y separadas por unos días. Las firma él. Ninguna llama la atención, porque cada una cuadra, lleva su número y trae su fecha y su proveedor.

El problema solo asoma al mirar las tres facturas a la vez, cosa que nadie hace, porque el libro de un año trae miles de líneas y quien lo revisa tiene una jornada de ocho horas. Pasa igual con la factura pagada dos veces, o con el proveedor que cobra sin que nadie encuentre un papel suyo archivado. Ahí está la parte difícil del oficio: apuntar lo que pasó es rutina, mientras que dar con lo que desentona entre miles de apuntes correctos exige mirar el libro entero de golpe.

### Qué hay dentro

Un repositorio es una carpeta de trabajo publicada en internet con todo su historial de cambios. Este contiene cuatro programas, un libro de asientos inventado y dos textos de explicación.

Le entregas un libro y te devuelve una lista de líneas que conviene mirar de cerca. Pasa ocho pruebas y ninguna acusa a nadie, porque cada una propone candidatos para que después una persona los examine con el expediente delante. Un candidato no es una condena.

Todo lo que hace son cuentas, sin inteligencia artificial dentro, sin base de datos y sin nada que instalar. El proyecto del que salió esta pieza sí funciona con modelos de lenguaje, y necesitaba debajo algo que comprobara sumando y diera siempre el mismo resultado.

### Los conceptos

Se llama **determinista** a la prueba que contesta siempre lo mismo ante la misma entrada. Sumar lo es, mientras que preguntarle a un modelo de lenguaje no lo es, porque el mismo texto puede dar hoy una respuesta y mañana otra parecida. Aquí las ocho pruebas son deterministas, así que su resultado se puede repetir y discutir delante de un auditor.

**Control interno** es el conjunto de reglas que una empresa se pone para que sus cuentas sean fiables, y **COSO** es el marco más usado para ordenarlas. Tiene cinco componentes, de los cuales aquí solo uno es código que se ejecuta: el tercero, las actividades de control. Los demás quedan como contexto, salvo el cuarto, que aparece marcado como parcial. Conviene fijarse en esa franqueza, porque un proyecto que dijera cubrir los cinco estaría vendiendo humo.

Para entender la prueba más famosa hace falta un rodeo. Coge las facturas de un año y apunta solo con qué cifra empieza cada importe. ¿Cuántas empezarán por 1 y cuántas por 9? El instinto dirá que una novena parte cada una, alrededor del 11 %, y en esto el instinto falla de lleno. En cualquier conjunto de cifras que abarque desde decenas hasta decenas de miles, el 1 sale como primera cifra el 30,1 % de las veces y el 9 apenas el 4,6 %.

Fíjate en un importe que crece y verás la razón. Cien euros tienen que doblarse para dejar atrás el 1 y llegar a 200, mientras que a 900 le basta con subir un 11 % para volver otra vez al 1. Un importe pasa mucho más tiempo empezando por 1 que por 9, y una lista de facturas es la foto de muchos importes repartidos por ese recorrido. Ese reparto se llama **ley de Benford**.

La relación con el fraude está en que quien se inventa cifras nunca las inventa siguiendo esa curva natural. Escribe importes creíbles, casi siempre pegados al límite que puede aprobar él solo, de modo que esos importes empiezan una y otra vez por las mismas dos cifras. La curva lo nota aunque cada factura, mirada por separado, parezca normal.

Cada prueba trae además su **control negativo**, que es una lista de casos normales que la prueba tiene prohibido marcar. Piensa en una factura de venta con su cobro, que toca la misma cuenta y la misma referencia dos veces y por eso parece un duplicado. No lo es. ¿Por qué se le dedica tanto sitio a lo que no hay que marcar? Porque una alarma que salta sin motivo acaba desconectada, y un detector desconectado protege menos que ninguno.

Quedan cuatro nombres por aclarar. El **fraccionamiento** es partir un pago grande en varios parecidos para que ninguno llegue al importe que exige una firma superior, y la literatura anglosajona lo llama *structuring*. El **tercero fantasma** es una cuenta de proveedor o de cliente que mueve dinero sin ninguna referencia ni factura detrás. El **casi-duplicado** es el pago repetido que se escapa del filtro exacto por un céntimo o por una referencia distinta. Los **huecos de secuencia** son saltos en la numeración de los asientos, que en un libro con numeración garantizada delatan un apunte desaparecido.

### El ejemplo

Todos los datos de ejemplo se los inventa un programa a partir de una **semilla fija**, que es el número con el que arranca el generador de azar, de modo que el libro sale idéntico en cada ejecución. Dentro hay siete fraudes plantados a mano y cuatro controles negativos, apuntados de antemano. Sobre ese libro conocido se comprueban las dos mitades: que la batería caza lo plantado y que deja en paz lo legítimo.

Así se ve una línea del libro:

```
1002,2026-01-25,40000004,0.0,348.63,FAC-C000,h9a06ae2da28a,COMPRA,2026-07-13,,MANUAL
```

De izquierda a derecha: número de asiento, fecha, cuenta, debe, haber, referencia del documento, huella de la factura, tipo de operación, vencimiento, fecha de cobro (aquí vacía) y origen.

Sobre esas líneas pasan las ocho pruebas, cada una desde una altura distinta. Basta una sola línea para revisar sus fechas, porque un cobro anterior a la fecha de su asiento resulta imposible en el tiempo. Los duplicados buscan la línea gemela en cualquier punto del libro, mientras que el pago partido, los redondos y el proveedor sin papeles agrupan por cuenta. Solo los huecos de numeración y la prueba de Benford necesitan leer el libro entero.

Al final, la demostración compara sus hallazgos con la lista de fraudes plantados y escribe el veredicto:

```
Clústeres: 1 -> [('40000009', 3, 9000.0)]
  [OK  ] caza el fraccionamiento sembrado (40000009, 3x3.000)
  [OK  ] control negativo: nóminas recurrentes NO son fraccionamiento
```

Ahí está la reforma del primer apartado: tres cargos de tres mil euros al mismo proveedor en cinco días, nueve mil en total, que es justo la suma que el director tendría que haber firmado.

### Las ocho pruebas

| Prueba | Qué huella busca | Sobre datos reales |
|---|---|---|
| Benford | El primer dígito de los importes se aleja de su curva natural | Accionable con volumen (más de 5.000) |
| Duplicados | La misma línea exacta repetida (referencia, cuenta, debe, haber) | Accionable siempre |
| Fraccionamiento | Importes parecidos al mismo tercero en pocos días | Accionable con datos reales |
| Casi-duplicado | El pago repetido que se escapa por un céntimo o una referencia | Accionable con datos reales |
| Tercero fantasma | Cuenta de tercero que mueve dinero sin rastro documental | Informativa (calidad de dato) |
| Coherencia de fechas | Un cobro o un vencimiento anteriores a la fecha del asiento | Accionable siempre |
| Redondos | Concentración anómala de importes redondos en una cuenta | Señal de apoyo |
| Huecos de secuencia | Saltos en la numeración de asientos | Informativa (calidad de dato) |

### El marco de control interno

Las pruebas se ordenan dentro del marco COSO, en su versión ligera. La tabla enseña qué parte de cada componente es código que se ejecuta y qué parte es contexto.

| Componente (COSO) | Qué vigila | En este repo |
|---|---|---|
| 1. Entorno de control | Reglas y responsabilidades claras | Marco: se describe |
| 2. Evaluación de riesgos | Dónde puede colarse un error o un fraude | Marco: se describe |
| 3. Actividades de control | Las pruebas concretas que detectan la anomalía | **Ejecutable**: la batería de arriba |
| 4. Información y comunicación | La pista de auditoría (quién hizo qué y cuándo) | Parcial: el dato existe, aquí se explota |
| 5. Supervisión | Revisar que los controles siguen vivos | Marco: se describe |

Hay una pieza a caballo entre el entorno y las actividades, la **segregación de funciones**, que consiste en que quien genera un asiento no sea quien lo aprueba. Existe en el flujo y se puede auditar, y aquí queda marcada como parcial porque el repositorio la comprueba sin inventarla.

### Qué está medido

Cifras obtenidas ejecutando el repositorio el 22/07/2026 con Python 3.14.6:

| Comprobación | Resultado |
|---|---|
| `probar_todo.py` | termina bien: 39 comprobaciones verdes, ninguna roja |
| Autotest sin datos · batería sobre el libro | 27 verdes · 12 verdes |
| Libro generado | 116 líneas, semilla 20260713 |
| Duplicados · pago partido | `FAC-DUP-91` · cuenta `40000009`, 3 líneas, 9.000,00 |
| Casi duplicados | 2 grupos, uno de ellos el anterior |
| Proveedor sin papeles · fechas imposibles | cuenta `41000005` · `FAC-INC-01` |
| Redondos | cuenta `62900099`, 6 redondos de 7 líneas |
| Huecos de numeración | 112 entre el asiento 1002 y el 1229 |
| Benford, chi cuadrado | 3,9 en la muestra limpia y 4.724,5 en la manipulada |

### Lo que no sale tan bien como parece

La primera cosa la ve cualquiera al final del bloque de Benford. La prueba separa de sobra las dos muestras de cuatro mil importes, porque en la limpia el 1 encabeza el 29,6 % de ellos, muy cerca del 30,1 % previsto, mientras que en la manipulada el 1 cae al 14,6 % y el 4 sube al 30,0 % con el 5 en el 28,8 %. Para poner número a esa distancia se usa el **chi cuadrado**, que suma lo que se aparta cada cifra de lo previsto: la muestra limpia da 3,9 y la manipulada 4.724,5. Aun con esa separación, la puerta de tamaño responde `NO_APLICA` en la línea siguiente, porque cuatro mil importes se quedan por debajo de los cinco mil que exige la profesión. La demostración enseña así la capacidad con una muestra que ella misma declara insuficiente para acusar.

Vienen después los huecos, que salen 112 sobre 116 asientos, cifra enorme que no significa nada, porque el generador va saltando números al azar mientras crea el libro. Con encontrar un hueco cualquiera la comprobación ya se pone verde, así que sobre estos datos no mide nada, y `caso_real.md` lo reconoce dejando la prueba como informativa.

La tercera la escribe el propio autor. Los tres pagos de tres mil euros aparecen a la vez como pago partido y como casi duplicado, y se dejan así a propósito, porque esconderlo fingiría una precisión que no existe.

Hay una cuarta que el repositorio no enseña en ningún sitio, y sale de aplicar Benford a los ciento dieciséis importes del propio libro. El chi cuadrado da 8,9 y el 1 aparece treinta veces donde la curva esperaba 34,9, diferencia que con tan pocas líneas es ruido puro.

### Cuándo no sirve

Dos de las ocho pruebas están marcadas como informativas en la tabla de arriba, y una tercera solo como señal de apoyo. Que un proveedor no tenga papeles archivados suele responder a un apunte antiguo mal documentado, o a una migración hecha con prisa, de modo que tratarlo como fraude sería el error de bulto del proyecto. Los huecos solo valen sobre un libro cuya numeración esté garantizada como contigua.

Benford queda fuera de juego en una contabilidad pequeña. Fíjate en el subconjunto de importes elegidos a mano, que es donde miraría quien defrauda: suele tener unas decenas de líneas, muy lejos de los cinco mil necesarios.

### Frontera honesta

El motor calcula y propone. Decidir si un candidato es un error, un descuido o un fraude corresponde a una persona con el expediente encima de la mesa, y el porqué de que varias pruebas sean informativas a propósito está contado sin adornos en [caso_real.md](caso_real.md).

### Pruébalo

```bash
python probar_todo.py
```

Ejecuta el autotest de las funciones puras, genera el libro sintético y pasa la batería completa en un segundo. No hace falta instalar nada. Las mismas pruebas se ejecutan también en el servidor de GitHub con dos versiones de Python.

### Estructura

```
control-interno-fraude-ia/
  control/         motor.py (las pruebas, funciones puras) + demo.py
  datos_ejemplo/   generar_libro.py (libro SINTÉTICO con fraude sembrado) + CSV
  caso_real.md     las decisiones honestas: por qué varias pruebas no acusan
  probar_todo.py   autotest + genera datos + demo, todo de una vez
```

### Datos y privacidad

Todo es sintético y reproducible con semilla fija. No hay ningún dato real ni personal, ni ninguna conexión a una base de datos. El motor solo lee, sin escribir nada en ningún sitio.

### Repos relacionados

Este repo es la pieza de **control interno** de una serie sobre construir y evaluar sistemas de IA en los que se puede confiar:

- [accounting-agent-swarm](https://github.com/jleonceo/accounting-agent-swarm): el enjambre de agentes que lleva la contabilidad de principio a fin.
- [tesoreria-forecast-ia](https://github.com/jleonceo/tesoreria-forecast-ia): previsión de caja con backtesting, ratios y aging.
- [verificacion-determinista-ia](https://github.com/jleonceo/verificacion-determinista-ia): comprobar la coherencia del estado por pura aritmética, sin IA.
- [llm-eval-contable](https://github.com/jleonceo/llm-eval-contable): evaluar una skill contable como se examina a un alumno.
- [gobernanza-skills-analiticas](https://github.com/jleonceo/gobernanza-skills-analiticas): las reglas para gobernar skills sin que se descontrolen.
- [orquestacion-enjambres-ia](https://github.com/jleonceo/orquestacion-enjambres-ia): el enrutado multi-agente, a qué agente va cada petición sin romper al crecer.
- [agent-memory-governance](https://github.com/jleonceo/agent-memory-governance): que la memoria del agente no se convierta en un vertedero.
- [tu-primer-asistente-ia-web](https://github.com/jleonceo/tu-primer-asistente-ia-web): qué es un asistente de IA, para quien empieza de cero.

---

## English

### The problem

Picture a company with a rule anyone understands: purchases above three thousand euros are signed by the director, and below that the area manager's signature is enough. The rule exists so that nobody moves large sums without a second pair of eyes on them.

In comes the purchasing manager, who orders a nine thousand euro refurbishment and asks the supplier for three invoices of three thousand, with different numbers and a few days apart. He signs them himself. None of them draws attention, because each one adds up, carries its number and shows its date and its supplier.

The problem only surfaces when the three invoices are looked at together, which nobody does, because a year's ledger holds thousands of lines and whoever reviews it works an eight-hour day. The same goes for the invoice paid twice, or for the supplier who gets paid without anyone finding a single filed document. That is the hard part of the trade: recording what happened is routine, whereas spotting what is out of place among thousands of correct entries requires looking at the whole ledger at once.

### What is inside

A repository is a working folder published on the internet together with its full history of changes. This one holds four programs, an invented ledger and two explanatory texts.

You hand it a ledger and it returns a list of lines worth a closer look. It runs eight tests and none of them accuses anybody, because each one proposes candidates for a person to examine afterwards with the file in front of them. A candidate is not a conviction.

Everything it does is arithmetic, with no artificial intelligence inside, no database and nothing to install. The project this piece came out of does work with language models, so it needed something underneath that checked by adding up and always gave the same answer.

### The concepts

A test is called **deterministic** when it answers the same thing every time for the same input. Adding up is deterministic, whereas asking a language model is not, because the same text can give one answer today and a similar one tomorrow. All eight tests here are deterministic, so their result can be repeated, argued about and taken in front of an auditor.

**Internal control** is the set of rules a company gives itself so that its accounts are reliable, and **COSO** is the most widely used framework for organising them. It has five components, of which only one here is code that runs: the third, the control activities. The rest remain as context, except the fourth, which appears marked as partial. That frankness is worth noticing, because a project claiming to cover all five would be selling smoke.

Understanding the most famous test takes a detour. Take a year of invoices and write down only the digit each amount starts with. How many will begin with 1 and how many with 9? Instinct says a ninth each, around 11 %, and on this one instinct is badly wrong. In any set of figures spanning from tens to tens of thousands, 1 appears as the leading digit 30.1 % of the time and 9 barely 4.6 %.

Look at an amount as it grows and you will see the reason. One hundred euros has to double before it leaves the 1 behind and reaches 200, whereas 900 only needs to climb 11 % to come back round to 1. An amount spends far more time starting with 1 than with 9, and a list of invoices is a snapshot of many amounts spread along that path. That spread is called **Benford's law**.

Its link to fraud is that whoever invents figures never invents them following that natural curve. They write believable amounts, almost always pressed against the limit they can approve on their own, so those amounts begin over and over with the same two digits. The curve notices it even when each invoice, looked at on its own, seems normal.

Every test also ships its **negative control**, which is a list of normal cases the test is forbidden to flag. Think of a sales invoice together with its collection, which touches the same account and the same reference twice and therefore looks like a duplicate. It is not. Why devote so much room to what must not be flagged? Because an alarm going off for no reason ends up switched off, and a switched-off detector protects less than none at all.

Four names are left to clear up. **Fractioning** means splitting a large payment into several similar ones so that none reaches the amount requiring a higher signature, and the English-language literature calls it *structuring*. A **phantom party** is a supplier or customer account moving money with no reference or invoice behind it. A **near-duplicate** is the repeated payment that escapes the exact filter by a cent or by a different reference. **Sequence gaps** are jumps in the numbering of entries, which in a ledger with guaranteed numbering betray an entry that has vanished.

### The example

All the example data is invented by a program starting from a **fixed seed**, which is the number the randomness generator starts from, so the ledger comes out identical on every run. Inside there are seven frauds planted by hand and four negative controls, written down in advance. Over that known ledger both halves are checked: that the battery catches what was planted and that it leaves the legitimate cases alone.

This is what one line of the ledger looks like:

```
1002,2026-01-25,40000004,0.0,348.63,FAC-C000,h9a06ae2da28a,COMPRA,2026-07-13,,MANUAL
```

From left to right: entry number, date, account, debit, credit, document reference, invoice fingerprint, operation type, due date, collection date (empty here) and origin.

The eight tests pass over those lines, each from a different height. A single line is enough to review its dates, because a collection earlier than the date of its own entry is impossible in time. Duplicates look for the twin line anywhere in the ledger, whereas the split payment, the round amounts and the supplier without paperwork group by account. Only the numbering gaps and the Benford test need to read the whole ledger.

At the end, the demonstration compares its findings against the list of planted frauds and writes the verdict:

```
Clústeres: 1 -> [('40000009', 3, 9000.0)]
  [OK  ] caza el fraccionamiento sembrado (40000009, 3x3.000)
  [OK  ] control negativo: nóminas recurrentes NO son fraccionamiento
```

There is the refurbishment from the first section: three charges of three thousand euros to the same supplier within five days, nine thousand in total, which is exactly the sum the director should have signed off.

### The eight tests

| Test | What trace it looks for | On real data |
|---|---|---|
| Benford | The leading digit drifts from its natural curve | Actionable with volume (over 5,000) |
| Duplicates | The same exact line repeated (reference, account, debit, credit) | Always actionable |
| Fractioning | Similar amounts to the same party within a few days | Actionable on real data |
| Near-duplicate | The repeated payment that escapes by a cent or a reference | Actionable on real data |
| Phantom party | Third-party account moving money with no documentary trace | Informative (data quality) |
| Date coherence | A collection or due date earlier than the entry date | Always actionable |
| Round amounts | Anomalous concentration of round amounts in one account | Supporting signal |
| Sequence gaps | Jumps in the entry numbering | Informative (data quality) |

### The internal-control framework

The tests sit inside the COSO framework, in its light version. The table shows which part of each component is code that runs and which part is context.

| Component (COSO) | What it watches | In this repo |
|---|---|---|
| 1. Control environment | Clear rules, roles and responsibilities | Frame: described |
| 2. Risk assessment | Where an error or fraud can slip in | Frame: described |
| 3. Control activities | The concrete tests that detect the anomaly | **Runnable**: the battery above |
| 4. Information and communication | The audit trail (who did what and when) | Partial: the data exists, exploited here |
| 5. Monitoring | Checking the controls are still alive | Frame: described |

There is a piece straddling environment and activities, **segregation of duties**, which means whoever creates an entry is not whoever approves it. It exists in the flow and can be audited. The repository marks it partial because it checks the segregation without inventing it.

### What has been measured

Figures obtained by executing the repository on 22/07/2026 with Python 3.14.6:

| Check | Result |
|---|---|
| `probar_todo.py` | finishes cleanly: 39 green checks, none red |
| Autotest without data · battery over the ledger | 27 green · 12 green |
| Generated ledger | 116 lines, seed 20260713 |
| Duplicates · split payment | `FAC-DUP-91` · account `40000009`, 3 lines, 9,000.00 |
| Near-duplicates | 2 groups, one of them the previous case |
| Supplier without paperwork · impossible dates | account `41000005` · `FAC-INC-01` |
| Round amounts | account `62900099`, 6 round out of 7 lines |
| Numbering gaps | 112 between entry 1002 and entry 1229 |
| Benford, chi-square | 3.9 on the clean sample and 4,724.5 on the manipulated one |

### What does not hold up as well as it looks

The first thing is visible to anyone at the end of the Benford block. The test separates the two samples of four thousand amounts by a wide margin, because in the clean one the digit 1 leads 29.6 % of them, very close to the 30.1 % predicted, whereas in the manipulated one the 1 falls to 14.6 % and the 4 climbs to 30.0 % with the 5 at 28.8 %. To put a number on that distance the **chi-square** is used, which adds up how far each digit departs from the prediction: the clean sample gives 3.9 and the manipulated one 4,724.5. Even with that separation, the size gate answers `NO_APLICA` on the very next line, because four thousand amounts fall below the five thousand the profession requires. The demonstration therefore shows the capability with a sample it declares insufficient to accuse.

Next come the gaps, which come out at 112 over 116 entries, an enormous figure that means nothing, because the generator skips numbers at random while building the ledger. Finding any gap at all already turns the check green, so over this data it measures nothing, and `caso_real.md` admits it by leaving the test as informative.

The third one is written by the author himself. The three payments of three thousand euros show up at once as a split payment and as a near-duplicate, and they are left that way on purpose, because hiding it would fake a precision that does not exist.

There is a fourth point the repository shows nowhere, which comes from applying Benford to the one hundred and sixteen amounts of the ledger itself. The chi-square gives 8.9 and the digit 1 appears thirty times where the curve expected 34.9, a difference that with so few lines is pure noise.

### When it does not work

Two of the eight tests are marked as informative in the table above, and a third only as a supporting signal. A supplier without filed paperwork usually reflects an old badly documented entry, or a migration done in a hurry, so treating it as fraud would be the project's blunder. The gaps are only worth anything over a ledger whose numbering is guaranteed to be contiguous.

Benford is out of play in a small set of accounts. Look at the subset of hand-picked amounts, which is where a fraudster would be operating: it usually holds a few dozen lines, far away from the five thousand required.

### Honest boundary

The engine computes and proposes. Deciding whether a candidate is an error, an oversight or a fraud belongs to a person with the file on the table, and the reason why several tests are informative on purpose is told plainly in [caso_real.md](caso_real.md).

### Try it

```bash
python probar_todo.py
```

It runs the pure-function autotest, generates the synthetic ledger and passes the full battery in one second. Nothing to install. The same tests also run on GitHub's server against two versions of Python.

### Structure

```
control-interno-fraude-ia/
  control/         motor.py (the tests, pure functions) + demo.py
  datos_ejemplo/   generar_libro.py (SYNTHETIC ledger with seeded fraud) + CSV
  caso_real.md     the honest calls: why several tests do not accuse
  probar_todo.py   autotest + generate data + demo, all at once
```

### Data and privacy

Everything is synthetic and reproducible with a fixed seed. There is no real or personal data, and no database connection. The engine only reads, writing nothing anywhere.

### Related repositories

This repo is the **internal control** piece of a series on building and evaluating AI systems you can trust:

- [accounting-agent-swarm](https://github.com/jleonceo/accounting-agent-swarm): the agent swarm that runs the books end to end.
- [tesoreria-forecast-ia](https://github.com/jleonceo/tesoreria-forecast-ia): cash-flow forecasting with backtesting, ratios and aging.
- [verificacion-determinista-ia](https://github.com/jleonceo/verificacion-determinista-ia): checking state coherence by pure arithmetic, without AI.
- [llm-eval-contable](https://github.com/jleonceo/llm-eval-contable): evaluating an accounting skill the way you examine a student.
- [gobernanza-skills-analiticas](https://github.com/jleonceo/gobernanza-skills-analiticas): the rules for governing skills before they run wild.
- [orquestacion-enjambres-ia](https://github.com/jleonceo/orquestacion-enjambres-ia): multi-agent routing, which agent handles each request without breaking as it grows.
- [agent-memory-governance](https://github.com/jleonceo/agent-memory-governance): keeping the agent's memory from turning into a junkyard.
- [tu-primer-asistente-ia-web](https://github.com/jleonceo/tu-primer-asistente-ia-web): what an AI assistant is, for absolute beginners.

---

*Licencia / License: [MIT](LICENSE). Datos sintéticos, sin información real ni personal. Synthetic data, no real or personal information.*
