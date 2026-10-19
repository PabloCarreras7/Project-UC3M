# Caso 1.3 - Segmentación socio-sanitaria de Madrid

Carpeta del caso 1.3 del proyecto. El objetivo es agrupar los 21 distritos de Madrid según su perfil de riesgo y su contexto social, cruzando el socioeconómico con las activaciones del SAMUR.

## Archivos

- `limpieza_socioeconomico.ipynb` -> `socioeconomico_limpio.csv` (21 filas)
- `limpieza_distritos.ipynb` -> `distritos_limpio.csv` (21 filas)
- `limpieza_activaciones.ipynb` -> `activaciones_limpio.csv` (152.107 filas)
- `cruces_datasets.ipynb` -> `tabla_distritos.csv` (21 filas, una por distrito: la tabla que entra al clustering)

## Orden de ejecución

1. `limpieza_socioeconomico.ipynb`
2. `limpieza_distritos.ipynb` (rellena huecos con `socioeconomico_limpio.csv`)
3. `limpieza_activaciones.ipynb`
4. `cruces_datasets.ipynb` (usa los tres CSV limpios)

Los notebooks leen el CSV original de la carpeta `data` del repo (o junto al notebook) y guardan el limpio en esta carpeta. Cada celda de texto explica el porqué de cada decisión.

## Distritos

`distritos.csv` es la tabla maestra: id, nombre, código postal, población, superficie, hospitales y base del SAMUR. Traía 24 filas para 21 distritos.

- Nombres normalizados con una regla (mayúsculas, sin tildes; si el texto es el principio de un único nombre oficial, se completa). Sin diccionarios cerrados, como pidió Bluetab: lo que no encaje se queda sin tocar y se lista.
- Centro, Tetuán y Chamartín salían dos veces. Las copias no se contradicen, así que se juntan en una fila con el id original (1-21); la primera copia de Centro no tenía población y se completa con la de la otra copia.
- Moratalaz tenía población -999 (valor centinela): se pasa a vacío y se recupera cruzando con el socioeconómico (95.840). Igual para San Blas-Canillejas y las superficies de Retiro y Salamanca.
- Barajas no tiene población en ninguna tabla: se estima como densidad x superficie (47.703), la misma estimación que en el socioeconómico. Pendiente de confirmar.

## Socioeconómico

`socioeconomico.csv` trae los indicadores sociales de cada distrito. Traía 24 filas para 21 distritos.

- Misma regla de nombres que en distritos.
- `num_centros_salud` venía como texto: "ocho" pasa a 8 y "N/A" a vacío (no sabemos el número y no lo inventamos).
- Centro, Tetuán y Salamanca salían dos veces y se juntan rellenando huecos. La única contradicción es la densidad de Centro (28.626,8 frente a 28.627,0): diferencia de redondeo, nos quedamos el primer valor.
- Valores imposibles que pasan a vacío: % de mayores de 65 negativo (Chamartín y Ciudad Lineal), paro por encima de 100 (Moncloa-Aravaca y Hortaleza), población -999 (Barajas) y vulnerabilidad 1,5 (Carabanchel, asumiendo que el índice va de 0 a 1: pendiente de confirmar).
- Quedan 10 huecos sin rellenar (renta de Retiro y Ciudad Lineal, % de mayores de 65 de Chamartín y Ciudad Lineal, paro de Moncloa-Aravaca, Hortaleza y Villa de Vallecas, vulnerabilidad de Carabanchel y Barajas, centros de salud de San Blas-Canillejas). No hay fuente en el proyecto para ellos y no los inventamos: van a las preguntas para Bluetab.

## Activaciones

Hemos limpiado `activaciones.csv` para que los datos tengan el mismo formato. El resultado es un CSV con **152.107 filas y las 12 columnas originales**, sin añadir columnas de control.

- **Meses:** nombres en inglés, abreviaturas y números pasan a nombres de mes en español y mayúsculas, para que un mismo mes no aparezca como varias categorías.
- **Horas:** `hora_solicitud` y `hora_intervencion` unificadas a `HH:MM:SS`. Las horas que no constan se mantienen vacías, porque no podemos saber cuál era su valor.
- **Textos:** tipos de emergencia, distritos y hospitales en mayúsculas, sin tildes y sin espacios sobrantes, uniendo abreviaturas y nombres equivalentes.
- **Prioridad:** tres valores, `ALTA`, `MEDIA` y `BAJA` (`1 = ALTA`, `2 = MEDIA`, `3 = BAJA`, `URGENTE = ALTA`, `NORMAL = MEDIA`). Bluetab ha confirmado este criterio.
- **Edad:** se mantienen los valores entre 0 y 115 años; las edades fuera de ese rango pasan a nulo, sin borrar la fila ni sustituirlas por una media. Es el rango elegido para tratar edades poco creíbles y Bluetab lo ha aceptado.
- **Datos que faltan:** en hospital, sexo, tipo de emergencia, distrito y prioridad usamos `NO CONSTA`. En hospital no usamos `SIN TRASLADO`, porque que el campo esté vacío no demuestra que no hubiera traslado.
- **Hospital 12 de Octubre:** nombre unificado como `HOSPITAL 12 DE OCTUBRE` para no mantener varias formas del mismo hospital.
- **Vallecas:** `VALLECAS PTE.`, `P. VALLECAS` y `PUENTE DE VALLECAS` se agrupan como Puente de Vallecas; `VILLA DE VALLECAS` se mantiene aparte. Las 39 filas que solo dicen `VALLECAS` pasan a `NO CONSTA`, porque no hay información para elegir entre los dos distritos.
- **Duplicados:** 737 copias idénticas eliminadas (de 152.844 a 152.107 filas). Si un `activacion_id` se repite con datos distintos, conservamos las filas porque no sabemos cuál es la correcta.
- **Registros fuera de los distritos de Madrid:** se mantienen en esta limpieza. El filtro territorial se hace al preparar los datos para el clustering (en `cruces_datasets.ipynb`).

## Cruces entre datasets

`cruces_datasets.ipynb` revisa qué datasets se pueden cruzar y monta `tabla_distritos.csv`: una fila por distrito con perfil social, demanda y oferta sanitaria. Es la tabla que entra al clustering.

- **Socioeconómico + distritos:** encajan 21 de 21 por `distrito_id`.
- **Activaciones por distrito:** nº de activaciones, activaciones por 1.000 habitantes (para que los distritos grandes no parezcan peores solo por tener más gente), % de prioridad alta y edad media de los pacientes. Las 876 filas con distrito `NO CONSTA` y las 201 de fuera del término municipal cuentan en la demanda total, pero no se asignan a ningún distrito.
- **unidades_samur: sí.** Encaja el 100% por `unidad_id` (por id, no por código, que se repite). Da la carga por unidad y las unidades de cada distrito.
- **bases_samur y hospitales: sí.** Oferta por distrito: bases, unidades, hospitales y camas.
- **tipos_emergencia: todavía no.** Encaja el 92%, pero `INTOXICACION ETILICA` y `CAIDA` salen dos veces con categoría y prioridad distintas (14.223 activaciones afectadas). Hasta que Bluetab diga cuál manda, no se une.
- **accidentes: no para el clustering.** Es de tráfico, incluye municipios de fuera de Madrid y le faltan distritos. Posible ampliación (riesgo vial).
- **meteorología y calendario: no se puede.** Van por día y las activaciones no tienen día, así que no hay cruce por fecha.

## Pendiente (preguntas para Bluetab)

- **Regla de medianoche:** cuando la intervención es anterior a la solicitud puede ser un cruce de medianoche o un error. La indicación es sumar 24 horas solo en los cruces que encajen en la regla y dejar el tiempo a nulo en el resto, sin eliminar la activación. Falta concretar y validar la regla; después se calculará el tiempo de respuesta y se añadirá el tiempo medio por distrito a la tabla.
- **Día de la activación:** el archivo no incluye el día de solicitud ni de intervención, solo año, mes y horas. Bluetab ha confirmado que ese dato no existe en la fuente, así que no lo hemos inventado. Sin él no se pueden cruzar meteorología ni calendario.
- **63 `activacion_id` repetidos con datos distintos:** conservamos las dos filas. ¿Cuál es la versión correcta?
- **Hospital vacío** (99.787 filas, el 65%) como `NO CONSTA`: ¿vale ese criterio?
- **tipos_emergencia duplicados** (`INTOXICACION ETILICA` y `CAIDA`): ¿qué versión es la correcta?
- **Huecos del socioeconómico:** renta de Retiro y Ciudad Lineal, % de mayores de 65 de Chamartín y Ciudad Lineal, paro de Moncloa-Aravaca, Hortaleza y Villa de Vallecas, vulnerabilidad de Carabanchel y Barajas, centros de salud de San Blas-Canillejas. ¿Hay fuente oficial para rellenarlos?
- **Índice de vulnerabilidad:** hemos asumido que va de 0 a 1. ¿Es correcto?
- **Población de Barajas:** estimada como densidad x superficie (47.703). ¿Tienen el dato real?
