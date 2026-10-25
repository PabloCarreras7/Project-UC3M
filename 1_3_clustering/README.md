# Caso 1.3 - Segmentación socio-sanitaria de Madrid

Caso 1.3 del proyecto. El objetivo es agrupar los 21 distritos de Madrid según su perfil de riesgo y su contexto social, cruzando el socioeconómico con las activaciones del SAMUR.

## Archivos utilizados y resultados

- `limpieza_socioeconomico.ipynb` -> `socioeconomico_limpio.csv` (21 filas)
- `limpieza_distritos.ipynb` -> `distritos_limpio.csv` (21 filas)
- `limpieza_activaciones.ipynb` -> `activaciones_limpio.csv` (152.107 filas, 13 columnas)
- `cruces_datasets.ipynb` -> `tabla_distritos.csv` (21 filas, una por distrito) y `tabla_distritos_norm.csv` (la misma tabla con las columnas numéricas en escala 0-1: la que entra al clustering)
- `socioeconomico_normalizado.csv`: el socioeconómico limpio con las columnas numéricas en escala 0-1

## Orden de ejecución

1. `limpieza_socioeconomico.ipynb`
2. `limpieza_distritos.ipynb` (rellena huecos con `socioeconomico_limpio.csv`)
3. `limpieza_activaciones.ipynb`
4. `cruces_datasets.ipynb` (usa los tres CSV limpios)

Los notebooks leen los CSV originales y generan los CSV limpios sin modificar los originales. Cada celda de texto explica el porqué de cada decisión.

## Distritos

`distritos.csv` es la tabla maestra: id, nombre, código postal, población, superficie, hospitales y base del SAMUR. Traía 24 filas para 21 distritos.

- Nombres normalizados con una regla (mayúsculas, sin tildes; si el texto es el principio de un único nombre oficial, se completa). Sin diccionarios cerrados, como pidió Bluetab: lo que no encaje se queda sin tocar y se lista.
- Centro, Tetuán y Chamartín salían dos veces. Las copias no se contradicen, así que se juntan en una fila con el id original (1-21); la primera copia de Centro no tenía población y se completa con la de la otra copia.
- Moratalaz tenía población -999 (valor centinela): se pasa a vacío y se recupera cruzando con el socioeconómico (95.840). Igual para San Blas-Canillejas (162.715) y las superficies de Retiro (5,46 km²) y Salamanca (5,41 km²).
- Barajas no tiene población en ninguna tabla: se estima como densidad x superficie (47.703), la misma estimación que en el socioeconómico. Es una estimación, no un dato real.
- `num_hospitales` y `base_samur` se dejan como vienen. Se comparan con los catálogos de hospitales y bases en `cruces_datasets.ipynb` y no coinciden en varios distritos (ver Cruces entre datasets).
- El CSV original no se toca: el limpio se guarda aparte.

## Socioeconómico

`socioeconomico.csv` trae los indicadores sociales de cada distrito. Traía 24 filas para 21 distritos.

- Misma regla de nombres que en distritos.
- `num_centros_salud` venía como texto: "ocho" pasa a 8 con una regla que descompone la palabra-número y suma sus partes (decena + unidad), no con una lista cerrada de equivalencias, como pidió Bluetab. "N/A" pasa a vacío (no sabemos el número y no lo inventamos).
- Centro, Tetuán y Salamanca salían dos veces y se juntan rellenando huecos (así Tetuán recupera el índice de vulnerabilidad, 0,55, y sus 6 centros de salud). La única contradicción es la densidad de Centro (28.626,8 frente a 28.627,0): diferencia de redondeo, nos quedamos el primer valor.
- Valores imposibles que pasan a vacío: % de mayores de 65 negativo (Chamartín y Ciudad Lineal), paro por encima de 100 (Moncloa-Aravaca y Hortaleza), población -999 (Barajas) y vulnerabilidad 1,5 (Carabanchel, asumiendo que el índice va de 0 a 1, que es donde está el resto de distritos). Los rangos que usamos son: porcentajes de 0 a 100, vulnerabilidad de 0 a 1, edad media de 15 a 90, y población, superficie, renta y densidad por encima de 0.
- Los dos valores de paro por encima de 100 (118,1 y 116,3) podrían ser 11,8 y 11,6 con la coma desplazada, pero no lo podemos comprobar, así que no se corrigen: quedan vacíos.
- Había 10 huecos sin dato (renta de Retiro y Ciudad Lineal, % de mayores de 65 de Chamartín y Ciudad Lineal, paro de Moncloa-Aravaca, Hortaleza y Villa de Vallecas, vulnerabilidad de Carabanchel y Barajas, centros de salud de San Blas-Canillejas). No hay fuente en el proyecto, y con 21 distritos no podemos quitar ninguno del clustering, así que los rellenamos con una regla: la media de los 3 distritos más parecidos que sí tienen el dato (vecinos más cercanos, k=3). Para medir lo parecidos que son se usan los indicadores sociales en la misma escala y solo los que el distrito tiene; en los centros de salud se añade la población. Es una suposición nuestra, no un dato real; el notebook enseña con qué distritos se calcula cada valor. Ya no queda ningún valor vacío en `socioeconomico_limpio.csv`, y `tabla_distritos.csv` ya lleva los valores rellenos.
- Las columnas vienen en escalas muy distintas (la renta va de 23.000 a 71.000 y la vulnerabilidad de 0 a 1), así que para el clustering cada columna numérica se pasa a escala 0-1 con min-max y se guarda aparte en `socioeconomico_normalizado.csv`. El limpio original no se toca.

## Activaciones

Hemos limpiado `activaciones.csv` para que los datos tengan el mismo formato. El resultado es un CSV con **152.107 filas y 13 columnas**: las 12 originales más `tiempo_respuesta_min` (minutos de respuesta). Sin columnas de control.

- **Meses:** nombres en inglés, abreviaturas y números pasan a nombres de mes en español y mayúsculas, para que un mismo mes no aparezca como varias categorías.
- **Horas:** `hora_solicitud` y `hora_intervencion` unificadas a `HH:MM:SS`. Las horas que no constan se mantienen vacías, porque no podemos saber cuál era su valor.
- **Textos:** tipos de emergencia, distritos y hospitales en mayúsculas, sin tildes y sin espacios sobrantes, uniendo abreviaturas y nombres equivalentes.
- **Prioridad:** tres valores, `ALTA`, `MEDIA` y `BAJA` (`1 = ALTA`, `2 = MEDIA`, `3 = BAJA`, `URGENTE = ALTA`, `NORMAL = MEDIA`). Bluetab lo confirmó por correo (14/10): es un problema de estandarización, no de significado.
- **Edad:** se mantienen los valores entre 0 y 115 años; las edades fuera de ese rango pasan a nulo, sin borrar la fila ni sustituirlas por una media. Bluetab confirmó por correo (14/10) que 0-115 es válido y que se acepta cualquier límite razonable y justificado; lo que no se acepta es dejar edades negativas o imposibles sin tratar.
- **Datos que faltan:** en hospital, sexo, tipo de emergencia, distrito y prioridad usamos `NO CONSTA`. En hospital no usamos `SIN TRASLADO`, porque que el campo esté vacío no demuestra que no hubiera traslado.
- **Hospital 12 de Octubre:** nombre unificado como `HOSPITAL 12 DE OCTUBRE` para no mantener varias formas del mismo hospital.
- **Vallecas:** `VALLECAS PTE.`, `P. VALLECAS` y `PUENTE DE VALLECAS` se agrupan como Puente de Vallecas; `VILLA DE VALLECAS` se mantiene aparte. Bluetab confirmó por correo (14/10) que esas variantes son Puente y que el único valor ambiguo es `VALLECAS` a secas (39 filas), que podíamos excluir del análisis por distrito o asignar al distrito más frecuente, documentándolo. En la reunión del 15/10 comentaron que quizá se podía resolver con otros datasets. Lo probamos (ver abajo) y no se puede, así que esas 39 filas pasan a `NO CONSTA`.
- **Duplicados:** 737 copias idénticas eliminadas (de 152.844 a 152.107 filas). Si un `activacion_id` se repite con datos distintos, conservamos las filas porque no sabemos cuál es la correcta.
- **Cruces de medianoche:** 610 filas traían la intervención antes que la solicitud (616 antes de quitar duplicados, el número que también tenía Bluetab). Siguiendo su correo (14/10): asumimos que solicitud e intervención son del mismo día salvo cruce de medianoche, y nuestra regla es solicitud entre las 20:00 y las 23:59 e intervención entre las 00:00 y las 06:59, que suma 24 horas (569 filas). Las 41 que no encajan son errores de registro: el tiempo de respuesta queda vacío pero la activación se conserva. Los límites salen de los propios datos: el 92% de esas filas pide a las 23 horas y el 95% interviene a las 00, y con esos límites todas las duraciones resultantes son posibles según los tiempos del mismo día (la mayor es de unas 5 horas; los tiempos del mismo día llegan a 11). El detalle está en `limpieza_activaciones.ipynb`.
- **Registros fuera de los distritos de Madrid:** se mantienen en esta limpieza. El filtro territorial se hace al preparar los datos para el clustering (en `cruces_datasets.ipynb`).

### Vallecas a secas: qué probamos y por qué lo dejamos en NO CONSTA

El detalle con los números está en `limpieza_activaciones.ipynb` (sección "Vallecas a secas").

- **Unidades SAMUR:** miramos la base de la unidad que atendió cada activación. En el resto de distritos con base solo coincide con el distrito de la activación el 11% de las veces (más o menos una de cada ocho, como si fuera al azar), y las 39 filas se reparten entre las mismas bases que las de Puente y Villa. No sirve.
- **Hospital:** solo 15 de las 39 filas tienen hospital (9 Gregorio Marañón y 5 Infanta Leonor) y los dos hospitales reciben activaciones de Puente y de Villa. Da una probabilidad, no una certeza.
- **Accidentes, meteorología y calendario:** no comparten ninguna clave con esas filas.
- **Por qué no las asignamos a Puente (el más frecuente, 72%):** sería inventar el dato, porque seguro que una parte son de Villa. Son el 0,03% de las filas, así que dejarlas fuera del análisis por distrito casi no cambia nada, y siguen contando en la demanda total.

## Cruces entre datasets

`cruces_datasets.ipynb` revisa qué datasets se pueden cruzar y monta `tabla_distritos.csv`: una fila por distrito con perfil social, demanda y oferta sanitaria. Es la tabla que entra al clustering.

- **Socioeconómico + distritos:** encajan 21 de 21 por `distrito_id`.
- **Activaciones por distrito:** nº de activaciones, activaciones por 1.000 habitantes (para que los distritos grandes no parezcan peores solo por tener más gente), % de prioridad alta, edad media de los pacientes y tiempo medio de respuesta (ya con la regla de medianoche aplicada). Las 876 filas con distrito `NO CONSTA` y las 201 de fuera del término municipal cuentan en la demanda total, pero no se asignan a ningún distrito.
- **unidades_samur: sí.** Encaja el 100% por `unidad_id` (por id, no por código, que se repite). Da la carga por unidad y las unidades de cada distrito.
- **bases_samur y hospitales: sí.** Oferta por distrito: bases, unidades, hospitales y camas. Los catálogos escriben el distrito de otra forma (`LA LATINA`, `FUENCARRAL`, `VALLECAS`), así que se normaliza con una regla (quitar el artículo y completar si el texto es el principio de un único distrito oficial), sin diccionarios. Las unidades se buscan solo entre los distritos con base, y así `VALLECAS` encaja en Puente de Vallecas. Lo que no encaja (hospitales de otros municipios y el Hospital Infanta Leonor, cuyo distrito es solo `VALLECAS`) se lista y se deja fuera. Un distrito que no sale en un catálogo (sin base, sin unidades o sin hospital) cuenta 0 en esa columna, porque el catálogo no tiene registros suyos; es una suposición nuestra y así la tabla no tiene huecos. Un hospital que sí sale pero sin dato de camas (Fundación Jiménez Díaz, en Arganzuela) no se cuenta como 0 camas: se le pone la media de camas de los hospitales que sí tienen el dato (876).
- **Comprobación con `distritos.csv`:** `num_hospitales` no coincide con el catálogo de hospitales en 12 de 21 distritos, y `base_samur` no coincide con el catálogo de bases en 6 de 21. No corregimos ninguna de las dos fuentes y la tabla usa los catálogos.
- **Normalización 0-1:** igual que en el socioeconómico, las columnas numéricas de la tabla pasan a escala 0-1 con min-max y se guardan en `tabla_distritos_norm.csv`, que es la que entra al clustering. Como la oferta ya trae 0 donde no hay recursos, la tabla normalizada no tiene valores vacíos. Si una columna fuera constante (mismo valor en todos los distritos) se deja en 0, porque no distingue distritos y el min-max daría error.
- **tipos_emergencia: todavía no.** Encaja el 92%, pero `INTOXICACION ETILICA` y `CAIDA` salen dos veces con categoría y prioridad distintas (14.223 activaciones afectadas). Como no hay forma de saber cuál de las dos versiones es la correcta, no se une el catálogo; para los tipos más frecuentes se usa el texto de la propia activación.
- **accidentes: no para el clustering.** Es de tráfico, incluye municipios de fuera de Madrid y le faltan distritos. Posible ampliación (riesgo vial).
- **meteorología y calendario: no se puede.** Van por día y las activaciones no tienen día: el dato abierto del SAMUR solo publica año, mes y horas (Bluetab lo confirmó por correo el 14/10), así que no hay cruce por fecha. Es una limitación del dato, no algo que podamos inventar.
