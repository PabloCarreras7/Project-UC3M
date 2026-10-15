# Limpieza de activaciones

Hemos limpiado `activaciones.csv` para que los datos tengan el mismo formato y se puedan usar después en el análisis del caso 1.3.

El resultado de la limpieza es un CSV con **152.107 filas y las 12 columnas originales**, sin añadir columnas de control. El notebook recoge los pasos, las comprobaciones y los estadísticos finales.

## Cambios realizados

- **Meses:** hemos pasado los nombres en inglés, las abreviaturas y los números a nombres de mes en español y mayúsculas. Así, un mismo mes no aparece como varias categorías.
- **Horas:** hemos unificado `hora_solicitud` y `hora_intervencion` al formato `HH:MM:SS`, cambiando puntos y guiones por dos puntos y añadiendo los ceros que faltaban. Las horas que no constan se mantienen vacías, porque no podemos saber cuál era su valor.
- **Textos:** hemos pasado los tipos de emergencia, distritos y hospitales a mayúsculas y sin tildes, quitado espacios al principio y al final y unido abreviaturas y nombres equivalentes. Esto evita contar como distintos valores que significan lo mismo.
- **Prioridad:** hemos dejado tres valores: `ALTA`, `MEDIA` y `BAJA`. La equivalencia es `1 = ALTA`, `2 = MEDIA`, `3 = BAJA`, `URGENTE = ALTA` y `NORMAL = MEDIA`. Bluetab ha confirmado este criterio.
- **Edad:** hemos mantenido los valores entre 0 y 115 años. Las edades fuera de ese rango pasan a nulo, sin borrar la fila ni sustituirlas por una media. Es el rango elegido para tratar edades poco creíbles y Bluetab lo ha aceptado.
- **Datos que faltan:** en hospital, sexo, tipo de emergencia, distrito y prioridad usamos `NO CONSTA`. En hospital no usamos `SIN TRASLADO`, porque que el campo esté vacío no demuestra que no hubiera traslado.
- **Hospital 12 de Octubre:** hemos unificado su nombre como `HOSPITAL 12 DE OCTUBRE` para no mantener varias formas del mismo hospital.
- **Vallecas:** `VALLECAS PTE.`, `P. VALLECAS` y `PUENTE DE VALLECAS` se agrupan como Puente de Vallecas; `VILLA DE VALLECAS` se mantiene aparte. Las 39 filas que solo dicen `VALLECAS` pasan a `NO CONSTA`, porque no hay información para elegir entre los dos distritos. Se conservan en el CSV, pero no se pueden asignar a un distrito en ese análisis.
- **Duplicados:** después de unificar los formatos, hemos eliminado 737 copias idénticas en todas las columnas, pasando de 152.844 a 152.107 filas. Si un `activacion_id` se repite con datos distintos, conservamos las filas porque no sabemos cuál es la correcta.
- **Registros fuera de los distritos de Madrid:** se mantienen en esta limpieza. El filtro territorial se hará al preparar los datos para el clustering.

## Lo que queda pendiente

El archivo no incluye el día de solicitud ni de intervención, solo año, mes y horas. Bluetab ha confirmado que ese dato no existe en la fuente, así que no lo hemos inventado.

Cuando la hora de intervención es anterior a la de solicitud, puede haber un cruce de medianoche o un error. Todavía no hemos aplicado una corrección ni calculado un tiempo de respuesta definitivo. Falta concretar y validar la regla en la reunión con Bluetab. Su indicación es sumar 24 horas solo en los cruces que encajen en la regla y dejar el tiempo a nulo en el resto, sin eliminar la activación.

## Archivos y uso

- `limpieza_activaciones.ipynb`: notebook con la limpieza, sus razones y las salidas guardadas.
- `activaciones_limpio-920ebca6.csv`: CSV limpio que está en esta carpeta. Su contenido coincide con el resultado del notebook; el nombre conserva el sufijo del archivo subido.

Para volver a ejecutar el notebook, hace falta el `activaciones.csv` original del proyecto junto al notebook o en `../data/activaciones.csv`. No se debe usar el CSV limpio como entrada. Al ejecutarlo se genera `activaciones_limpio.csv`.
