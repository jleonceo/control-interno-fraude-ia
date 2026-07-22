# control-interno-fraude-ia

**Cazar fraude contable con aritmética, y callar sobre lo que es normal.**
**Catching accounting fraud with arithmetic, and staying quiet about what is normal.**

Sin dependencias (solo Python estándar), sin base de datos, sin IA, sin red.
No dependencies (standard Python only), no database, no AI, no network.

[Español](#español) · [English](#english)

---

## Español

### Qué resuelve

Registrar lo que pasó es la parte fácil de la contabilidad. La difícil es mirar un libro
de miles de asientos y decir dónde hay algo que no encaja: un pago colado dos veces, una
factura partida para no llamar la atención, una cuenta que mueve dinero sin ningún papel
detrás. Este repositorio enseña a **detectar esas anomalías con comprobaciones deterministas**,
sin IA, y a hacerlo sin ahogar al auditor en falsas alarmas.

La idea de fondo es que el fraude deja huellas aritméticas. Quien inventa cifras rompe la
curva natural de los primeros dígitos. Quien parte un pago deja tres importes parecidos muy
juntos en el tiempo. Quien paga dos veces deja dos líneas casi calcadas. Cada una de esas
huellas tiene una prueba que la busca, y cada prueba trae su **control negativo**: la lista
de lo que NO se marca, para no confundir lo normal con lo sospechoso.

### El marco de control interno

Las pruebas no van sueltas. Se ordenan dentro de un marco de control interno de los que se
usan de verdad (COSO, en su versión ligera). El marco tiene cinco componentes; aquí se ve
qué parte de cada uno es código que se ejecuta y qué parte es contexto:

| Componente (COSO) | Qué vigila | En este repo |
|---|---|---|
| 1. Entorno de control | Reglas y responsabilidades claras | Marco: se describe |
| 2. Evaluación de riesgos | Dónde puede colarse un error o un fraude | Marco: se describe |
| 3. Actividades de control | Las pruebas concretas que detectan la anomalía | **Ejecutable**: la batería de abajo |
| 4. Información y comunicación | La pista de auditoría (quién hizo qué y cuándo) | Parcial: el dato existe, aquí se explota |
| 5. Supervisión | Revisar que los controles siguen vivos | Marco: se describe |

El corazón que se ejecuta es el componente 3: las **actividades de control**, es decir, la
batería forense. Los demás componentes son el encuadre que da sentido a esas pruebas. Y hay
una pieza a caballo entre el entorno y las actividades, la **segregación de funciones** (que
quien genera un asiento no sea quien lo aprueba): existe en el flujo y se puede auditar, pero
aquí se marca como parcial porque no se inventa, se comprueba.

### Las pruebas (código puro y reproducible que pasa en verde)

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

Ninguna prueba acusa. Cada una **propone candidatos** para que una persona los mire. Un
candidato no es una condena.

### El ejemplo

El repositorio trae un **libro de asientos sintético** generado con semilla fija, así que
es idéntico en cada ejecución y se sabe de antemano qué esconde. Dentro hay fraude sembrado
a propósito (un duplicado, un fraccionamiento, un casi-duplicado, una cuenta fantasma, una
incoherencia de fechas, una concentración de redondos y huecos de numeración) y también
controles negativos legítimos (una factura con su cobro, nóminas recurrentes, deuda con
importes redondos por naturaleza). La demo comprueba dos cosas a la vez: que la batería
**caza todo el fraude sembrado** y que **no marca ninguno de los casos legítimos**.

### Pruébalo

```bash
python probar_todo.py
```

Ejecuta el autotest de las funciones puras, genera el libro sintético y pasa la batería
completa. No hace falta instalar nada.

### Estructura

```
control-interno-fraude-ia/
  control/         motor.py (las pruebas, funciones puras) + demo.py
  datos_ejemplo/   generar_libro.py (libro SINTÉTICO con fraude sembrado) + CSV
  caso_real.md     las decisiones honestas: por qué varias pruebas no acusan
  probar_todo.py   autotest + genera datos + demo, todo de una vez
```

### Datos y privacidad

Todo es sintético y reproducible (semilla fija). No hay ningún dato real ni personal, ni
ninguna conexión a una base de datos. El motor solo lee; no escribe nada en ningún sitio.

### Frontera honesta

El motor calcula y propone. La decisión de si un candidato es un error, un descuido o un
fraude es de una persona, con el expediente delante. Varias pruebas son informativas a
propósito, y el porqué está contado sin adornos en [caso_real.md](caso_real.md).

### Repos relacionados

Este repo es la pieza de **control interno** de una serie sobre construir y evaluar sistemas
de IA en los que se puede confiar:

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

### What it solves

Recording what happened is the easy part of accounting. The hard part is looking at a ledger
of thousands of entries and saying where something does not fit: a payment slipped in twice,
an invoice split to stay under the radar, an account moving money with no paperwork behind
it. This repository shows how to **detect those anomalies with deterministic checks**, no AI,
and to do it without drowning the auditor in false alarms.

The underlying idea is that fraud leaves arithmetic traces. Whoever invents figures breaks
the natural curve of leading digits. Whoever splits a payment leaves three similar amounts
close together in time. Whoever pays twice leaves two near-identical lines. Each trace has a
test that looks for it, and each test ships its **negative control**: the list of what is NOT
flagged, so the normal is not mistaken for the suspicious.

### The internal-control framework

The tests are not loose. They sit inside a real internal-control framework (COSO, in its
light version). The framework has five components; here you can see which part of each is
code that runs and which is context:

| Component (COSO) | What it watches | In this repo |
|---|---|---|
| 1. Control environment | Clear rules, roles and responsibilities | Frame: described |
| 2. Risk assessment | Where an error or fraud can slip in | Frame: described |
| 3. Control activities | The concrete tests that detect the anomaly | **Runnable**: the battery below |
| 4. Information and communication | The audit trail (who did what and when) | Partial: the data exists, exploited here |
| 5. Monitoring | Checking the controls are still alive | Frame: described |

The runnable heart is component 3: the **control activities**, that is, the forensic battery.
The other components are the framing that gives those tests meaning. And there is a piece
between environment and activities, **segregation of duties** (whoever creates an entry is not
whoever approves it): it exists in the flow and can be audited, but here it is marked partial
because it is not invented, it is checked.

### The tests (pure and reproducible code that passes green)

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

No test accuses. Each one **proposes candidates** for a person to look at. A candidate is not
a conviction.

### The example

The repository ships a **synthetic ledger** generated with a fixed seed, so it is identical
on every run and its contents are known in advance. Inside there is fraud seeded on purpose
(a duplicate, a fractioning, a near-duplicate, a phantom account, a date incoherence, a round
amount concentration and numbering gaps) plus legitimate negative controls (an invoice with
its collection, recurring payroll, debt with round amounts by nature). The demo checks two
things at once: that the battery **catches all the seeded fraud** and that it **flags none of
the legitimate cases**.

### Try it

```bash
python probar_todo.py
```

It runs the pure-function autotest, generates the synthetic ledger and passes the full
battery. Nothing to install.

### Structure

```
control-interno-fraude-ia/
  control/         motor.py (the tests, pure functions) + demo.py
  datos_ejemplo/   generar_libro.py (SYNTHETIC ledger with seeded fraud) + CSV
  caso_real.md     the honest calls: why several tests do not accuse
  probar_todo.py   autotest + generate data + demo, all at once
```

### Data and privacy

Everything is synthetic and reproducible (fixed seed). There is no real or personal data, and
no database connection. The engine only reads; it writes nothing anywhere.

### Honest boundary

The engine computes and proposes. Deciding whether a candidate is an error, an oversight or
fraud belongs to a person, with the file in front of them. Several tests are informative on
purpose, and the reason is told plainly in [caso_real.md](caso_real.md).

### Related repositories

This repo is the **internal control** piece of a series on building and evaluating AI systems
you can trust:

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
