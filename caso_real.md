# El hallazgo honesto: no toda señal es una acusación

Un detector de fraude que grita a la primera pierde su valor. Si marca cientos de cosas
normales, el auditor deja de mirarlo, y entonces no sirve para nada. La parte difícil de
estas pruebas no es encontrar lo raro: es callar sobre lo normal. Aquí van las decisiones
honestas que tomó este motor, y que en un demo con datos limpios es fácil esconder.

## 1. "Sin rastro documental" es calidad de dato, no fraude

La prueba del tercero fantasma busca cuentas de proveedor o cliente que mueven dinero sin
ninguna referencia ni factura detrás. Suena a fraude, pero casi nunca lo es: lo normal es
que sea un apunte antiguo mal documentado, una migración, un asiento hecho con prisa. Por
eso la prueba es INFORMATIVA, no acusatoria. Señala la cuenta para que un humano la mire,
y solo sube a sospecha seria si se combina con otra señal (un importe alto, un tercero que
aparece una sola vez). Marcarla como fraude por sí sola sería el error de bulto del módulo.

## 2. Benford no se aplica a puñados de datos

La Ley de Benford es potente, pero la profesión pone un límite claro: por debajo de unos
5.000 registros no es fiable (Journal of Accountancy, 2022). En una contabilidad pequeña,
el subconjunto de importes elegidos a mano (que es donde miraría un defraudador) suele ser
de unas decenas o pocos cientos de líneas. Ahí Benford no aplica, y este motor lo dice en
voz alta en vez de reportar picos de ruido como si fueran hallazgos. La demo lo enseña al
revés: con 4.000 importes generados, distingue de sobra una muestra limpia de una
manipulada. La capacidad está; el gate decide cuándo usarla.

## 3. Varias pruebas demuestran capacidad, no fraude sobre estos datos

Sobre un libro sintético, los huecos de secuencia, las operaciones en fin de semana o los
importes parecidos entre sí son artefactos de cómo se generó, no señales de fraude. Estas
pruebas quedan como INFORMATIVAS: enseñan que el motor sabe detectarlas, y rendirán de
verdad cuando entren datos reales. Las accionables de verdad sobre cualquier libro son las
que no admiten excusa: un duplicado exacto, un cobro anterior a la fecha de su asiento.

## 4. Un solapamiento honesto

En la demo, la prueba de casi-duplicado también marca el clúster de fraccionamiento (tres
pagos de 3.000 al mismo proveedor). No es un error: tres cargos casi iguales en pocos días
son, a la vez, un fraccionamiento y un casi-duplicado. Dos pruebas distintas mirando el
mismo hecho desde dos ángulos. Se deja así a propósito, porque esconderlo sería fingir una
precisión que no existe.

## La frontera

El motor PROPONE candidatos. No decide, no acusa, no bloquea. La decisión de si un
candidato es un error, un descuido o un fraude es de una persona, con el expediente
delante. Esa frontera no está aquí por modestia: está porque es la única forma honesta de
usar una herramienta así.
