# Caso 1.3: registro completo y versión definitiva

## Dos notebooks y un solo registro de decisiones

`segmentacion_final_distritos.ipynb` es el notebook definitivo de todo el socioeconómico. `cruces_datasets.ipynb` permanece como segundo notebook definitivo, separado, y se ejecuta antes. Contiene TODO el recorrido socioeconómico: preparación y trazabilidad, interfaz con cruces, código completo del baseline 10D, exploración gráfica completa y modelo principal 9D con comparación 10D, pruebas, perfiles e interpretación. Este README conserva el registro detallado de qué se hizo y por qué; no sustituye la evidencia ejecutada dentro del notebook.

### Orden del análisis socioeconómico

- A. Decisiones de limpieza de distritos, socioeconómico y activaciones.
- B. Preparación y límites de los catálogos de recursos.
- C. Interfaz comprobada con `cruces_datasets.ipynb`, que construye las dos tablas distritales por separado.
- D. Baseline 10D completo, con diagnóstico y pruebas originales.
- E. Exploración socioeconómica completa: ritmos, tipos, edad registrada, demanda, contexto, oferta y mapas.
- F. Desarrollo final: selección de variables, algoritmos, k, 9D principal y 10D comparado, robustez, DBSCAN, siluetas individuales, mediana/P90, análisis directo de tipologías y conclusiones frente al enunciado.

### Dependencias y ejecución

Ejecutar de arriba abajo desde la raíz del repo o desde `1_3_clustering/`. Necesita los CSV comunes de `data_clean/`, el raw `data/accidentes.csv` para evaluar ese cruce y los límites geográficos. Las limpiezas comunes permanecen en `cleaning/` porque sirven al proyecto; no son versiones alternativas del análisis socioeconómico. Sus decisiones relevantes se explican en el notebook y en este README. Ninguno modifica los raw ni el CSV limpio de activaciones. Primero cruces regenera las tablas; después el análisis regenera figuras y verificaciones.

### Estructura y conservación

- `README.md`: este registro completo.
- `cruces_datasets.ipynb`: cruces completos y generación de tablas.
- `segmentacion_final_distritos.ipynb`: análisis socioeconómico integral ejecutado.
- `tabla_distritos.csv`, `tabla_distritos_norm.csv`: salidas intermedias reproducibles, no análisis alternativos.
- `graficos_cierre_9D/`: resultados del modelo principal y comparaciones finales.
- `graficos_recorrido_eda/`: gráficos regenerados de la exploración integrada.
- `graficos_cierre/`: exportaciones 10D previas, conservadas sin sobrescribir.
- `archivo/version_remota_dff7b22/`: fuentes originales de la rama, conservadas byte a byte. Incluye main.ipynb, que la lectura remota devuelve vacío.
- `archivo/antes_consolidacion_2026-11-17/`: copia íntegra de los notebooks/documentación preparados antes de esta consolidación. No es el punto de entrada. Para reproducir un notebook archivado se debe configurar el directorio de trabajo en su ubicación original: `1_3_clustering/` para baseline/cruces/cierre y `data_viz/` para la exploración histórica.
- `comparacion_edad.json`, `verificacion_resultados.json` y el GeoJSON: auxiliares, no versiones finales paralelas.
- PPTX/PDF: derivados del análisis ya revisado; mantienen los resultados 9D/10D, no sustituyen el recorrido completo del notebook.

No se elimina trabajo. Las dos carpetas de archivo distinguen la fuente remota original de los cambios preparados antes de consolidar; la integración solo adapta rutas y rótulos, no el algoritmo ni los datos. El original EDA común de `data_viz/` no se mueve porque está fuera de la carpeta del caso; queda como fuente histórica y toda su exploración está integrada aquí.

## Registro de preparación y cruces


Caso 1.3 del proyecto. El objetivo es agrupar los 21 distritos de Madrid según su perfil de riesgo y su contexto social, cruzando el socioeconómico con las activaciones del SAMUR.

## Archivos utilizados y resultados

- `limpieza_socioeconomico.ipynb` -> `socioeconomico_limpio.csv` (21 filas)
- `limpieza_distritos.ipynb` -> `distritos_limpio.csv` (21 filas)
- `limpieza_activaciones.ipynb` -> `activaciones_limpio.csv` (146.567 filas, 13 columnas)
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

**Procedencia:** esa atribución se conserva como anotación histórica no verificada; la regla se justifica por reproducibilidad y tratamiento explícito de ambigüedades.

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

Hemos limpiado `activaciones.csv` para que los datos tengan el mismo formato y le hemos aplicado el criterio del catálogo de tipos de emergencia. El resultado es un CSV con **146.567 filas y 13 columnas**: las 12 originales más `tiempo_de_respuesta` (duración de la respuesta en minutos). Sin columnas de control.

El nombre `tiempo_de_respuesta` sustituye al anterior `tiempo_respuesta_min`, que se confundía con `tiempo_respuesta_objetivo_min` del catálogo. Son dos cosas distintas: el nuestro es la duración observada de cada activación (intervención menos solicitud) y el del catálogo es el umbral que se espera cumplir para ese tipo de emergencia.

- **Meses:** nombres en inglés, abreviaturas y números pasan a nombres de mes en español y mayúsculas, para que un mismo mes no aparezca como varias categorías.
- **Horas:** `hora_solicitud` y `hora_intervencion` unificadas a `HH:MM:SS`. Las horas que no constan se mantienen vacías, porque no podemos saber cuál era su valor.
- **Textos:** distritos y hospitales en mayúsculas, sin tildes y sin espacios sobrantes, uniendo abreviaturas y nombres equivalentes. `tipo_emergencia` se normaliza igual en una primera pasada, y al final del notebook se sustituye por el código del catálogo (ver "Criterio del catálogo").
- **Prioridad:** tres valores, `alta`, `media` y `baja`, en minúsculas y **tomados del catálogo**, no del registro. En la primera pasada se estandarizan los valores del registro (`1 = ALTA`, `2 = MEDIA`, `3 = BAJA`, `URGENTE = ALTA`, `NORMAL = MEDIA`), como confirmó Bluetab por correo (14/10), pero esa prioridad solo coincide con la que el catálogo asigna al tipo en el 37,7% de las filas, que con tres clases está en el rango del azar. Como no deriva del tipo, manda el catálogo.

**Fuente y alcance:** fuentes primarias recuperadas en la sección de trazabilidad de correos. Las ventanas horarias, no imputar Vallecas y los valores del catálogo limpio siguen siendo decisiones propias, no una aprobación atribuible al remitente.

- **Edad:** se mantienen los valores entre 0 y 115 años; las edades fuera de ese rango pasan a nulo, sin borrar la fila ni sustituirlas por una media. Bluetab confirmó por correo (14/10) que 0-115 es válido y que se acepta cualquier límite razonable y justificado; lo que no se acepta es dejar edades negativas o imposibles sin tratar.

**Fuente y alcance:** fuentes primarias recuperadas en la sección de trazabilidad de correos. Las ventanas horarias, no imputar Vallecas y los valores del catálogo limpio siguen siendo decisiones propias, no una aprobación atribuible al remitente.

- **Datos que faltan:** en hospital, sexo y distrito usamos `NO CONSTA`. En hospital no usamos `SIN TRASLADO`, porque que el campo esté vacío no demuestra que no hubiera traslado. En tipo de emergencia y prioridad también se usa en la primera pasada, pero esas dos columnas acaban tomando el valor del catálogo, así que en el CSV final no queda ningún `NO CONSTA` en ellas.
- **Hospital 12 de Octubre:** nombre unificado como `HOSPITAL 12 DE OCTUBRE` para no mantener varias formas del mismo hospital.
- **Vallecas:** las variantes explícitas de Puente se unifican y Villa se mantiene aparte. Los 39 registros que en origen solo dicen VALLECAS se dejan sin asignar por falta de localización demostrable. Es cifra de origen, no recuento final tras filtros. El criterio definitivo es NO CONSTA y exclusión del análisis por distrito, sin asignar probabilísticamente.
- **Duplicados:** 737 copias idénticas eliminadas (de 152.844 a 152.107 filas). Si un `activacion_id` se repite con datos distintos, conservamos las filas porque no sabemos cuál es la correcta. Al unificar después los alias del catálogo aparecen 27 duplicados exactos más que antes eran invisibles porque el texto difería (una fila decía `PCR` y su pareja `PATOLOGIA CARDIOVASCULAR`); como los 27 pares comparten `activacion_id` y ya no se diferencian en nada, se eliminan con la misma regla. Quedan 25 `activacion_id` repetidos con contenido realmente distinto.
- **Cruces de medianoche:** 610 filas traían la intervención antes que la solicitud (616 antes de quitar duplicados, el número que también tenía Bluetab). Siguiendo su correo (14/10): asumimos que solicitud e intervención son del mismo día salvo cruce de medianoche, y nuestra regla es solicitud entre las 20:00 y las 23:59 e intervención entre las 00:00 y las 06:59, que suma 24 horas (569 filas). Las 41 que no encajan son errores de registro: el tiempo de respuesta queda vacío pero la activación se conserva. Los límites salen de los propios datos: el 92% de esas filas pide a las 23 horas y el 95% interviene a las 00, y con esos límites todas las duraciones resultantes son posibles según los tiempos del mismo día (la mayor es de unas 5 horas; los tiempos del mismo día llegan a 11). El detalle está en `limpieza_activaciones.ipynb`.

**Fuente y alcance:** fuentes primarias recuperadas en la sección de trazabilidad de correos. Las ventanas horarias, no imputar Vallecas y los valores del catálogo limpio siguen siendo decisiones propias, no una aprobación atribuible al remitente.

- **Registros fuera de los distritos de Madrid:** se mantienen en esta limpieza. El filtro territorial se hace al preparar los datos para el clustering (en `cruces_datasets.ipynb`).
- **Filas sin tipo de emergencia:** se eliminan 5.513 filas (el 3,62%) en las que `tipo_emergencia` no describe una urgencia (ver "Criterio del catálogo").

### Criterio del catálogo de tipos de emergencia

La primera pasada solo normaliza mayúsculas y tildes en `tipo_emergencia`, sin fusionar tipos por significado: eso necesitaba una revisión aparte del catálogo, que es la última parte del notebook. Al final, `tipo_emergencia` queda con los **39 códigos del catálogo**, escritos tal cual los escribe él (acentuados y en caja mixta, `Patología cardiovascular`), para que la columna sea literalmente igual a `tipos_emergencia_clean.codigo` y el cruce posterior sea directo.

- **Normalización para cruzar:** el catálogo va acentuado y en minúsculas y activaciones en mayúsculas sin tildes, así que un cruce literal solo resuelve 19 de los 104 tipos (el 27% de las filas). Normalizando acentos y caja sube al 93%.
- **Alias ortográficos** (597 filas): abreviaturas del mismo tipo, como `CARDIOVASCULAR`, `PAT. CARDIOVASCULAR`, `INTOX. ETILICA` o `HERIDA`. Siete están confirmadas por el propio dato: en el CSV original hay `activacion_id` repetidos donde las dos filas son la misma activación escrita de dos formas. `PCR` es la excepción: el dato lo empareja con `Patología cardiovascular`, pero es la sigla de Parada CardioRespiratoria y esa entrada existe aparte, así que manda el significado de la sigla. El criterio es idéntico en las dos, así que ningún dato cambia.
- **Alias agrupados:** el catálogo agrupa lo que activaciones registra separado. `MALTRATO A MENORES` y `MALTRATO A ANCIANOS` van a `Maltrato a menores y ancianos`; `AUTOLISIS TRAUMATICA` y `AUTOLISIS NO TRAUMATICA` a `Autolisis (traumática y no traumática)`; las patologías infecciosa, urológica, ginecológica y digestiva a `Patología médica no urgente (...)`. Esto resuelve cinco entradas del catálogo que antes no se usaban nunca.
- **Alias clínicos** (1.564 filas): tipos que sí son urgencias pero no tenían entrada propia, asignados al tipo catalogado al que se parecen para que hereden su criterio. `INFARTO O PATOLOGIA CORONARIA` a `Patología cardiovascular`, `ARROLLAMIENTO METRO Y/O TREN` a `Atropello`, `ARMA DE FUEGO` a `Arma blanca`, `EXPLOSION` a `Atrapamientos y derrumbamientos`. Sin esto caían en `Otros` y heredaban `baja / 20 min / sin médico`: había 426 infartos con objetivo de 20 minutos. Tres de estos mapeos pierden matiz y van avisados en el notebook: `ACCIDENTE SIN ESPECIFICAR` (no es una equivalencia, es el accidente más frecuente usado como defecto), `HERIDAS COMPLICADAS` y `ORDEN MEDICA URGENTE /AGRESIVO`.
- **A `Otros`** (48 filas): urgencias sin ningún equivalente razonable, `PROBLEMA SOCIAL`, `PACIENTE EN HUELGA DE HAMBRE` y `PERSONA "SIN TECHO" FALLECIDA EN VIA PUBLICA`.
- **Filas eliminadas** (5.513): hay 26 valores donde `tipo_emergencia` no dice qué le pasaba al paciente, sino el recurso enviado (`1 SVB` es una unidad de Soporte Vital Básico, `SVA` el Avanzado, `PMA` un Puesto Médico Avanzado), quién dio el aviso (`POLICIA NACIONAL`, `BOMBERO DE MADRID`), un servicio no asistencial (`PREVENTIVOS`, `SERVICIO DE LOGISTICA Y OTROS`) o el lugar (`VIA PUBLICA`, `DOMICILIO`). Son tres dimensiones distintas metidas en el mismo campo. El catálogo no les puede aplicar criterio porque no hay patología que buscar, y meterlas en `Otros` las mezclaría con urgencias reales de baja prioridad, así que se eliminan. La lista está en `tipos_sin_urgencia`, dentro del notebook. Con ellas se van las 18 filas que tenían la prioridad a `NO CONSTA` y el tipo tampoco informaba.
- **Correcciones al catálogo:** `Violencia de genero` pasa a requerir médico, como las otras dos entradas de `Violencia/Social` con el mismo `media / 12 min`; y `Agresión con spray de defensa` pasa de `baja / 20 / sin médico` a `media / 12 / con médico`, porque era la única agresión en `baja`. Se unifican tres pares que eran la misma cosa con criterio idéntico: `Caída` dentro de `Casual: caída, etc`, `Accidente de monopatin` y `Accidente de bicicleta` en `Accidente de bicicleta o monopatín`, y `Patología digestiva` dentro de la entrada de patología no urgente. El catálogo pasa de 42 a 39 entradas.
- **Comprobación final:** el cruce cierra en las dos direcciones. Ninguna fila se queda sin tipo del catálogo y ninguno de los 39 códigos se queda sin usar.

Bicicleta y moto siguen separadas a propósito: `Accidente de motocicleta` es `alta / 8 min / con médico` y `Accidente de bicicleta o monopatín` es `media / 12 min / sin médico`. Lo que se unificó fue bici con patinete.

### Vallecas a secas: qué probamos y por qué lo dejamos en NO CONSTA

El detalle con los números está en `limpieza_activaciones.ipynb` (sección "Vallecas a secas").

- **Unidades SAMUR:** miramos la base de la unidad que atendió cada activación. En el resto de distritos con base solo coincide con el distrito de la activación el 11% de las veces en la comprobación histórica, sin una correspondencia exclusiva entre base y distrito. No sirve.
- **Hospital:** el destino hospitalario no demuestra el lugar de la emergencia: un mismo hospital recibe pacientes de Puente y de Villa. No usamos ese destino para asignar el distrito de las filas ambiguas. Los 39 son registros del fichero de origen; no presentamos aquí un subtotal de supervivientes tras la limpieza.
- **Accidentes, meteorología y calendario:** no comparten ninguna clave con esas filas.
- **Por qué no las asignamos a Puente (el más frecuente, 72%):** sería inventar el dato, porque desconocemos el distrito real de cada fila. La cifra de 39 corresponde solo al origen. No cuantificamos su efecto final ni afirmamos cuántas sobreviven a los filtros sin una trazabilidad fila a fila. En el CSV limpio, las filas que sobreviven y quedan como NO CONSTA se incluyen en el total y se excluyen de la agregación por distrito.

## Cruces entre datasets

`cruces_datasets.ipynb` revisa qué datasets se pueden cruzar y monta `tabla_distritos.csv`: una fila por distrito con perfil social, demanda y oferta sanitaria. Es la tabla que entra al clustering.

- **Socioeconómico + distritos:** encajan 21 de 21 por `distrito_id`.
- **Activaciones por distrito:** nº de activaciones, activaciones por 1.000 habitantes (para que los distritos grandes no parezcan peores solo por tener más gente), % de prioridad alta, edad media de los pacientes y tiempo medio de respuesta (ya con la regla de medianoche aplicada). Las 567 filas con distrito `NO CONSTA`, las 33 de fuera del término municipal y la de `CARRETERAS Y CIRCUNVALACIONES` cuentan en la demanda total, pero no se asignan a ningún distrito.
- **unidades_samur: sí.** Encaja el 100% por `unidad_id` (por id, no por código, que se repite). Da la carga por unidad y las unidades de cada distrito.
- **bases_samur y hospitales:** se usan los catálogos limpios y se corrigen solo dos distritos con fuente oficial: Infanta Leonor a Villa de Vallecas y Jiménez Díaz a Moncloa-Aravaca (fuentes y evidencia en limpieza_hospitales.ipynb). Las 10 unidades VALLECAS no se asignan; no se imputan camas ni se mezclan series de distintos criterios. Cualquier agregado distrital con un hospital sin camas queda vacío. Los ceros solo significan ausencia de registros en el catálogo. Oferta excluida del clustering por decisión definitiva, no por una confirmación futura.
- **Comprobación con `distritos.csv`:** `num_hospitales` no coincide con el catálogo de hospitales en 12 de 21 distritos, y `base_samur` no coincide con el catálogo de bases en 6 de 21. No corregimos ninguna de las dos fuentes y la tabla usa los catálogos.
- **Normalización 0-1:** min-max por columna a 4 decimales; constantes a 0 y desconocidos conservados. Las 9 variables del modelo principal se comprueban finitas y coherentes con el escalado. Oferta excluida del clustering; detalle y evidencia en el notebook final.
- **tipos_emergencia: sí, ya resuelto.** Antes no se unía porque `INTOXICACION ETILICA` y `CAIDA` salían dos veces en el catálogo con categoría y prioridad distintas, y no había forma de saber cuál era la correcta. Eso se arregló en `limpieza_tipos_emergencia.py` (que deja una sola entrada de cada una) y en `limpieza_activaciones.ipynb`, donde se unifican los alias y se aplica el criterio del catálogo (ver "Criterio del catálogo"). Ahora `activaciones_limpio.csv` ya trae el tipo y la prioridad del catálogo, así que no hay que cruzar nada aquí: la columna `tipo_emergencia` es directamente `tipos_emergencia_clean.codigo`. Si se necesita la categoría, el tiempo objetivo o si requiere médico, se traen con un `merge` por esa columna.
- **accidentes: no para el clustering.** Es de tráfico, incluye municipios de fuera de Madrid y le faltan distritos. Posible ampliación (riesgo vial).
- **meteorología y calendario: no se puede.** Van por día y las activaciones no tienen día: el dato abierto del SAMUR solo publica año, mes y horas (Bluetab lo confirmó por correo el 14/10), así que no hay cruce por fecha. Es una limitación del dato, no algo que podamos inventar.

**Fuente y alcance:** fuentes primarias recuperadas en la sección de trazabilidad de correos. Las ventanas horarias, no imputar Vallecas y los valores del catálogo limpio siguen siendo decisiones propias, no una aprobación atribuible al remitente.



## Cierre vigente del análisis socioeconómico

El cierre está integrado en `segmentacion_final_distritos.ipynb`; el registro de cierre anterior se recoge más abajo en este mismo README. Modelo principal 9D sin edad registrada de paciente; comparación 10D ejecutada y conservada dentro del notebook. La exclusión se justifica con diagnóstico de distribución e influencia sobre grupos, no por buscar una métrica mayor. Se mantiene edad del censo. Gráficos principales en `graficos_cierre_9D/`; el baseline queda histórico. Las correcciones hospitalarias no alteraron las entradas 10D: los cambios de perfil posteriores se deben a la decisión de variable, no al catálogo.


## Registro de catálogos y decisiones de oferta


Limpieza de los tres catálogos de recursos que quedaban sin limpiar: `bases_samur.csv`, `hospitales.csv` y `unidades_samur.csv`. Un notebook por dataset en `cleaning/`, con cada decisión explicada, y un CSV limpio por cada uno en `data_clean/`. Los CSV originales no se tocan.

- `limpieza_bases_samur.ipynb` -> `bases_samur_limpio.csv` (15 filas)
- `limpieza_hospitales.ipynb` -> `hospitales_limpio.csv` (20 filas)
- `limpieza_unidades_samur.ipynb` -> `unidades_samur_limpio.csv` (60 filas)

Mismas reglas que en el resto de limpiezas del caso: normalización por reglas (mayúsculas, sin tildes, sin artículo del principio; un texto se completa solo si es el principio de una única categoría o distrito oficial), sin diccionarios cerrados. Lo que no se puede saber no se inventa: queda vacío, como `NO CONSTA` o con su texto original, y se documenta.

**Cruces actualizados el 17/11/2026:** dos correcciones geográficas oficiales en hospitales (Infanta Leonor a Villa y Jiménez Díaz a Moncloa). Las 10 unidades VALLECAS siguen sin asignar. La tabla deja vacías unidades en Puente/Villa y camas en Moncloa-Aravaca, donde falta Jiménez Díaz; los agregados de camas nunca suman parcialmente como si fueran capacidad total. No se imputa ni se mezclan cifras externas de 2024. Las 3 columnas de oferta quedan fuera del clustering como decisión definitiva. Evidencia y pruebas en limpieza_hospitales.ipynb, cruces_datasets.ipynb y segmentacion_final_distritos.ipynb.

## Bases (`bases_samur_limpio.csv`, 15 filas)

- **Distrito:** venía con mayúsculas y minúsculas mezcladas y un artículo (`La Latina`). Con la regla de siempre las 15 bases quedan con su distrito oficial.
- **Tipo de base:** solo cambiaba la escritura (`principal`, `PRINCIPAL`, `Secundaria`...). Quedan las 4 categorías reales: `PRINCIPAL`, `SECUNDARIA`, `SATELITE` y `AUXILIAR`. No hizo falta ninguna equivalencia.
- **Coordenadas imposibles:** la regla son los límites geográficos universales (latitud entre -90 y 90, longitud entre -180 y 180), no una caja alrededor de Madrid, y se revisa cada componente por separado. Base Hortaleza (latitud -95,2) y Base Barajas (latitud 91,5) tienen la latitud imposible y Base Moncloa la longitud (185). Solo pasa a vacío la componente imposible; la válida se conserva (la longitud de Hortaleza y Barajas y la latitud de Moncloa son datos reales). Esos tres pares quedan incompletos: la componente que falta no se inventa.
- **Año de apertura:** faltaba en 2 bases (Base Vallecas y Base Vicálvaro). No hay otra tabla del proyecto donde mirarlo, así que queda vacío. El año se deja como entero (venía como `1985.0`).
- No hay filas repetidas: las 15 filas se quedan.

## Hospitales (`hospitales_limpio.csv`, 20 filas)

- **Tipo:** solo cambiaba la escritura (`Público`, `PRIVADO`, `publico`...). Quedan las 3 categorías reales: `PUBLICO`, `PRIVADO` y `PRIVADO-CONCERTADO`.
- **Nombre corto:** mismo formato que el resto de textos (mayúsculas, sin tildes), para que un mismo hospital no aparezca escrito de dos formas.
- **Distrito o municipio:** 11 hospitales quedan asignados a distritos de Madrid en el catálogo limpio, incluido Infanta Leonor. Los otros 9 conservan su municipio. Esta es la clasificación del catálogo, no una validación completa de todas sus ubicaciones:
  - 9 son hospitales de otros municipios (Getafe, Móstoles, Alcorcón...): el dato es real, así que se conserva el nombre del municipio. Es la misma situación que en `accidentes.csv`: fuera del término municipal no hay datos socioeconómicos con los que cruzar, y en los cruces ya quedan fuera de la oferta por distrito.
  - El Hospital Infanta Leonor, hospital_id 13, se corrige a VILLA DE VALLECAS por su [dirección oficial](https://www.comunidad.madrid/hospital/infantaleonor/ciudadanos/llegar-contactar). Jiménez Díaz, hospital_id 8, se corrige de ARGANZUELA a MONCLOA-ARAVACA por el [directorio oficial](https://www.comunidad.madrid/centros/hospital-universitario-fundacion-jimenez-diaz). Solo CSV limpio, raw intacto; consulta 17/11/2026.
- **Camas:** cinco vacíos conservados, incluyendo dos valores imposibles (-50) tratados como desconocidos. No se usa media ni se completan con otra serie: el catálogo no especifica año/tipo de camas y difiere de [instaladas 2024, tabla 10 SERMAS](https://gestiona3.madrid.org/bvirtual/BVCM051700.pdf). La comparación completa y los perímetros hospitalarios están en limpieza_hospitales.ipynb. Los valores existentes se preservan como catálogo cuya homogeneidad no está validada; no entran al modelo.
- `urgencias_24h` y `helipad` ya venían bien (solo 0 y 1) y no se tocan.

## Unidades (`unidades_samur_limpio.csv`, 60 filas)

- **Clave buena:** `unidad_id` no se repite. El `codigo` se repite en 10 parejas: 8 se contradicen en algo (tipo, estado o kilómetros) y 2 son iguales en todo menos en el id. Como no podemos saber si esas 2 son la misma unidad registrada dos veces, se conservan todas las filas y se documenta, igual que en activaciones. Para cruzar: siempre por `unidad_id`, nunca por `codigo`.
- **Tipo de unidad:** venía con puntos y mayúsculas mezcladas (`UVI`, `U.V.I.`, `uvi`). Quitando puntos y poniendo mayúsculas quedan las 5 categorías reales: `UVI`, `SVB`, `VIR`, `MOTO` y `JEFATURA`. Las 8 filas sin tipo quedan vacías.
- **Estado:** se normaliza por escritura y `MANT` pasa a `MANTENIMIENTO` por la regla del principio único. `OK` se queda como categoría propia: seguramente quiera decir "operativa", pero no podemos comprobarlo y no inventamos la equivalencia. Categorías finales: `OPERATIVA`, `MANTENIMIENTO`, `BAJA`, `INACTIVA` y `OK`.
- **Distrito de la base:** misma regla de nombres. `FUENCARRAL` pasa a `FUENCARRAL-EL PARDO` (único distrito oficial que empieza así). **`VALLECAS` se queda como `VALLECAS`, sin asignar:** es principio de dos distritos y no hay fuente que diga a cuál pertenece cada unidad. Asignarlas a Puente por ser el único de los dos con base en el catálogo sería una inferencia (el catálogo podría estar incompleto), así que no se hace: en `tabla_distritos.csv` las unidades de Puente y de Villa de Vallecas quedan vacías (desconocidas), sin asignación definitiva por ausencia de evidencia suficiente; unidades excluidas del clustering. Las 5 unidades sin distrito quedan como `NO CONSTA`, igual que en activaciones.
- **Año de adquisición:** los datos se entregaron con el proyecto en septiembre de 2026 (correo de Bluetab del 15/09/2026). 2 unidades traen 2029, posterior a la propia entrega del dataset y con kilómetros ya registrados: imposible, pasa a vacío. Otras 2 traen 2026: la entrega del dataset no prueba la fecha de observación del catálogo, así que, sin evidencia para invalidarlo, se conservan. Tampoco asumimos que el catálogo sea una foto de 2024 solo porque las activaciones sean de 2024.

**Fuente y alcance:** fuentes primarias recuperadas en la sección de trazabilidad de correos. Las ventanas horarias, no imputar Vallecas y los valores del catálogo limpio siguen siendo decisiones propias, no una aprobación atribuible al remitente.

- **Kilómetros:** 5 unidades traen kilómetros negativos, imposible. Pasan a vacío. Los valores altos (máximo 1.447.628 km) se quedan: son muchos pero no imposibles, y no hay ninguna regla que los descarte.

## Huecos que quedan (resumen)

Ningún hueco se ha rellenado inventando datos:

- Bases: 3 componentes de coordenadas (2 latitudes y 1 longitud; los pares de esas 3 bases quedan incompletos) y 2 años de apertura.
- Hospitales: 5 camas.
- Unidades: 8 tipos de unidad, 5 distritos de base (`NO CONSTA`) más 10 `VALLECAS` sin asignar, 2 años y 5 kilómetros.


## Registro del cierre y de la decisión 9D


Material de cierre de la parte 1.3. El baseline `clustering_distritos.ipynb` se conserva como histórico; el modelo principal está en `segmentacion_final_distritos.ipynb`.

## Contenido y ejecución

El notebook final contiene carga y comprobaciones de integridad, selección de variables, escalado min-max, comparación KMeans/Ward/DBSCAN, elección de k, perfiles y mapas, robustez, análisis socioeconómico directo y conclusiones. Se ejecuta de arriba abajo después del notebook de cruces. Las comprobaciones `assert` detienen la ejecución si las entradas no cumplen lo esperado.

- Entradas: `tabla_distritos.csv`, `tabla_distritos_norm.csv`, `data_clean/activaciones_limpio.csv` y `data_clean/tipos_emergencia_clean.csv`.
- `graficos_cierre_9D/`: figuras principales 00-20, sensibilidad, diagnóstico de edad y comparación controlada.
- `graficos_cierre/`: exportaciones históricas 10D, conservadas sin sobrescribir.
- `distritos_madrid.geojson`: límites oficiales del Ayuntamiento de Madrid. El notebook los descarga si faltan.
- `comparacion_edad.json` y `verificacion_resultados.json`: resultados de comparación y comprobación.

## Decisiones

Las tres columnas de oferta (`unidades_samur`, `num_hospitales_cat`, `camas_hospital`) quedan fuera del clustering: hay unidades sin localización demostrable, camas sin año y definición comunes verificados, y la oferta no forma parte de los perfiles elegidos. No se imputan recursos. La oferta se describe aparte con lo conocido; las bases no demuestran cobertura operativa.

El principal tiene 9 variables, sin edad media registrada de paciente. Se mantiene el porcentaje de mayores de 65 años del censo. El diagnóstico muestra un patrón de edades casi uniforme cuya causa no conocemos y una influencia material sobre la partición. La exclusión no se decide por un rango pequeño ni solo por ganar silueta. La alternativa 10D se calcula y conserva dentro del mismo notebook.

KMeans usa k = 3, n_init = 50 y semilla 42. La elección combina silueta, codo e interpretación; la robustez se mide con ARI y no se presenta como universal. Las asociaciones son descriptivas, no causales ni pruebas de riesgo individual.

## Resultados y evidencia del 17/11/2026

- Principal 9D: silueta 0,274713; grupos de 9, 5 y 7 distritos, con 83.261, 29.203 y 33.502 activaciones.
- Comparación 10D: silueta 0,268310. ARI entre alternativas 0,729; Moncloa y San Blas pasan al perfil periférico al retirar edad registrada de paciente.
- Robustez 9D: ARI 1,00 entre semillas y sin Centro; 0,593 sin cuatro distritos con imputaciones; 0,331 frente a Ward; 0,608 sin densidad; 1,00 sin tiempo. Son contrapartidas relevantes: los perfiles son exploratorios y la muestra solo tiene 21 distritos.
- DBSCAN: rejilla de 44 configuraciones en cada espacio. En 9D hay cinco configuraciones multigrupo, con entre 6 y 15 distritos como ruido; ninguna divide los 21 en varios grupos sin excluir distritos. Se evita comparar su silueta parcial como si incluyera toda la muestra.
- PCA se utiliza para visualizar y se informa de la varianza representada; no determina los grupos.
- Se muestran silueta por distrito, mediana y P90 de respuesta con válidos/faltantes, renta y tipos de emergencia, vulnerabilidad y categorías, densidad y tiempos. Cada resultado lleva interpretación y límites junto a su salida.

Las dos correcciones geográficas de hospitales no alteran las entradas originales 10D. Dejan tres celdas de oferta desconocidas: unidades en Puente/Villa y camas en Moncloa. Los cambios posteriores de grupo proceden de excluir edad de paciente, no del catálogo hospitalario. No se modifican los CSV originales ni el CSV limpio de activaciones.


## Recorrido del baseline: decisiones y lectura de sus resultados

Registro del recorrido histórico integrado en el notebook socioeconómico. Las afirmaciones de provisionalidad describen esa fase; la selección vigente es 9D, con comparación 10D y contrapartidas explícitas en el cierre.

# Clustering de distritos (caso 1.3) - baseline exploratorio y diagnóstico

Avance de seguimiento: primer intento de clustering de los 21 distritos de Madrid para la segmentación socio-sanitaria. **Es un baseline exploratorio para discutir en el grupo, no un modelo validado ni una conclusión**: la separación entre grupos es modesta (ver las siluetas) y los perfiles de abajo son provisionales.

- **Entrada:** `tabla_distritos.csv` (valores reales) y `tabla_distritos_norm.csv` (misma tabla normalizada min-max 0-1). Ambas salen de `cruces_datasets.ipynb`.
- **Por qué normalizado:** k-means usa distancias euclídeas, así que sin escalar la renta (~40.000) aplastaría a los porcentajes (~0-30). La normalización min-max ya estaba hecha y validada en la fase de limpieza.
- **Reproducible:** `n_init=50` y `random_state=42` en todos los k-means; versiones al final.

**Cómo ejecutarlo:** abre el notebook dentro del repositorio y ejecuta todas las celdas en orden. Admite como carpeta de trabajo la raíz del repo o `1_3_clustering/`. No requiere descargar datos nuevos ni consultar servicios externos.

**Versión histórica 10D.** El modelo principal 9D y todas las decisiones actuales están en `segmentacion_final_distritos.ipynb`.

## 1. Carga y selección de variables

Regla aplicada, en este orden:

1. **Fuera las 3 columnas con datos desconocidos** (`unidades_samur`, `num_hospitales_cat`, `camas_hospital`): en la versión histórica tenían 7 celdas vacías; el cierre actual corrige dos ubicaciones hospitalarias y mantiene excluida la oferta, y el criterio acordado es no imputar lo que no se sabe. Está documentado en `README_recursos_samur.md`.
2. **Fuera `num_bases_samur`**: es oferta, y la oferta no debería decidir cómo se agrupan los distritos por su perfil socio-sanitario.
3. **Fuera columnas redundantes por construcción**: `poblacion` y `superficie_km2` (se prefiere densidad a tamaño absoluto, aunque la densidad no conserva toda la información de población y superficie) y `n_activaciones` (ya está en `activaciones_por_1000hab`, que es comparable entre distritos).
4. **Fuera las muy correlacionadas entre sí**: con 21 distritos, meter dos columnas casi idénticas cuenta esa dimensión dos veces. Se revisan los pares con |r| > 0,85 y se queda una representante por grupo.

Después se comprueba que no queda ningún hueco en la matriz del clustering (k-means no los admite).

Se ve que `renta_media_hogar`, `tasa_paro` e `indice_vulnerabilidad` miden casi lo mismo (r hasta 0,98), y `edad_media` y `pct_mayores_65` también (r = 0,98). Con la nueva limpieza de activaciones aparece además un par nuevo por encima del umbral: `densidad_hab_km2` ~ `tiempo_respuesta_medio_min` (r = 0,87). En este baseline se conservan ambas por representar geografía y servicio. La decisión definitiva y la prueba de sensibilidad están en segmentacion_final_distritos.ipynb. Se conservan `renta_media_hogar` como representante del eje económico y `pct_mayores_65` como representante del eje de edad, por ser las más directas de explicar. Las demás se descartan solo del clustering: siguen en la tabla y se usan al describir los grupos.

## 2. Elección de k: codo y silueta

Se prueba k de 2 a 8 con dos algoritmos: **k-means** (el sugerido en el enunciado) y **agrupamiento jerárquico con enlace Ward**. Se miran dos métricas:

- **Codo (inercia de k-means):** dónde deja de bajar fuerte la varianza interna.
- **Silueta:** cuánto se parece cada distrito a su grupo frente al vecino más cercano (mayor = mejor separado).

`num_centros_salud` se conserva como indicador del entorno sanitario general, no como disponibilidad operativa del SAMUR. Por tanto este baseline no agrupa solo por demanda: combina contexto socioeconómico, entorno sanitario y características de las activaciones. Los tiempos de respuesta y la tasa de activaciones entran en el modelo; las diferencias posteriores en esas variables describen la construcción de los grupos, no los validan de forma independiente.

**Lectura honesta:** el codo es gradual (no hay un salto claro) y la silueta máxima es ~0,27, una **separación modesta**: los distritos no forman grupos muy compactos y alejados. Dentro de esa modestia, k = 3 es donde la silueta es máxima para k-means (0,268); con Ward el máximo está en k = 2 (0,299) y k = 3 es la segunda opción (0,262), así que **k = 3 es el candidato provisional** para este baseline, no un número de grupos validado. k = 4 queda como alternativa a discutir.

Tener 21 filas no impide obtener una silueta alta. Aquí el valor absoluto sí advierte de solapamiento; la comparación entre k ayuda a elegir un candidato, pero no demuestra que existan grupos naturales.

## 3. Baseline: k-means con k = 3

## 4. Robustez del baseline (lo que aguanta y lo que no)

Antes de enseñar los perfiles, tres comprobaciones sobre la partición k = 3:

- **Sin Centro** (distrito atípico: su tasa de activaciones por 1.000 hab es aproximadamente el doble que la del segundo, ya vimos en el EDA que puede recoger demanda de visitantes y ocio nocturno, hipótesis que estos datos no permiten confirmar).
- **Sin los 4 distritos con valores imputados** en las variables usadas: la limpieza socioeconómica rellenó 10 huecos con la media de los 3 distritos más parecidos (kNN, k=3), una estimación metodológica, no un dato observado. De las variables del clustering, tocan la renta de Retiro y Ciudad Lineal, el % de mayores de 65 de Chamartín y Ciudad Lineal, y los centros de salud de San Blas-Canillejas.
- **Otras 19 semillas** para k-means (misma k y mismos datos).

**Resultado:** sin Centro y sin los distritos con imputaciones la partición se mantiene igual salvo reordenación de etiquetas (ARI = 1,00), y con las otras 19 semillas el ARI mínimo y mediano es 0,85. Es decir, **en estas pruebas concretas, al mantener el escalado original y k = 3, las asignaciones son bastante estables**, aunque ya no perfectas con todas las semillas. No demuestra independencia general de los datos imputados ni estabilidad ante cualquier cambio de muestra.

Lo que sí hay que decir con honestidad:

- La separación sigue siendo **modesta** (silueta global próxima a 0,27 en el baseline). Estos grupos son una forma razonable de resumir los distritos, no fronteras duras.
- Si quitamos del clustering los ejes económico y de edad enteros (renta y % de mayores de 65), la partición cambia bastante (ARI ≈ 0,46). Es esperable: esos ejes son gran parte del contenido del caso. Pero significa que el resultado **depende de variables que llevan 5 celdas imputadas (estimaciones, no observaciones)**; la sensibilidad se reporta en las pruebas anteriores.
- **La tabla mezcla todos los tipos de emergencia** sin distinguir: ahora todas las activaciones llevan el tipo y la prioridad del catálogo (39 códigos), pero no hay segmentación por tipo de emergencia todavía. Y ojo con `pct_prioridad_alta`: es la gravedad típica del tipo según el catálogo, no la prioridad registrada en cada evento.
- La población de Barajas es una estimación (densidad x superficie), no un dato real, y de ella depende su tasa de activaciones por habitante.

## 5. Perfil provisional de cada grupo (valores reales, no normalizados)

**Lectura provisional de los tres grupos** (resultado histórico del baseline; el cierre está en segmentacion_final_distritos.ipynb):

- **C0 - Denso y vulnerable** (Centro, Arganzuela, Tetuán, Latina, Carabanchel, Usera, Puente de Vallecas, Ciudad Lineal, Villaverde, San Blas-Canillejas): renta baja (33.000 € frente a 41.700 € de media), paro alto (12,6 %), más población extranjera (20,2 %) y donde se concentra la mayor parte de las activaciones registradas.
- **C1 - Acomodado y envejecido** (Retiro, Salamanca, Chamartín, Chamberí, Moncloa-Aravaca, Moratalaz): renta muy por encima de la media (56.300 €), paro bajo (7,2 %), el más envejecido (23,9 % de mayores de 65) y los mejores tiempos medios de respuesta (7,0 min).
- **C2 - Periférico y disperso** (Fuencarral-El Pardo, Hortaleza, Villa de Vallecas, Vicálvaro, Barajas): densidad muy baja (2.652 hab/km² frente a 14.410 de media), los peores tiempos medios de respuesta (9,7 min frente a 8,0 de media distrital; Barajas 10,7, Villa de Vallecas 10,0 y Vicálvaro 9,8 son los tres peores) y el mix de prioridad de catálogo más alto (46 % de tipos de prioridad alta, frente a 37 % en el C0). **No sabemos por qué**: podría deberse a distancias, cobertura, tráfico u otras causas; con estos datos no se puede distinguir, así que queda como observación descriptiva, no como explicación.

Cambio respecto a la versión anterior de la tabla: Moncloa-Aravaca pasa del grupo periférico al acomodado (su silueta ya no es negativa). Ojo con Centro: su tasa de activaciones por 1.000 hab (141,5) es más del doble que la del segundo distrito, y podría recoger demanda de visitantes y ocio nocturno; no podemos separar residentes y visitantes con estas tablas. Forma parte del C0, pero es un distrito atípico dentro de él (de ahí la comprobación A de la sección 4).

## 6. Oferta y demanda por grupo: solo descripción, sin conclusiones de cobertura

Lo único que se puede decir:

- El **C0** concentra la mayoría de las activaciones registradas (~89.300, el 61 %) y una tasa por habitante alta (47,9 por 1.000 hab, inflada por Centro).
- El **C1** tiene una tasa parecida (48,2) con solo 2 bases catalogadas para sus 6 distritos. No se puede interpretar como falta de cobertura: no sabemos las unidades reales, sus áreas de servicio ni cómo cubren los distritos vecinos.
- El **C2** tiene la tasa por habitante más baja (28,9) y, como se ha dicho, los peores tiempos medios de respuesta, sin que sepamos la causa.

La respuesta por grupo se calcula dando el mismo peso a cada distrito. **No es la media de todas sus activaciones**: para obtenerla harían falta los conteos de respuestas válidas por distrito, porque hay tiempos desconocidos. No se ajusta por gravedad, distancia o tráfico.

## 7. Diagnóstico por distrito: dónde se solapan los grupos

La silueta global puede ocultar asignaciones dudosas. Se calcula la silueta individual con la misma distancia euclídea que usa el clustering: cerca de 1 indica mayor separación, cerca de 0 indica frontera y por debajo de 0 indica que el distrito está, en promedio, más cerca de otro grupo. No es una probabilidad ni una medida de confianza estadística.

Se muestra además el Ward de k = 3 tras alinear sus etiquetas con k-means. Esa coincidencia compara dos algoritmos sobre los mismos datos: no es validación externa. No se descarta ningún distrito por tener silueta baja.

**Lectura de esta ejecución:** Hortaleza (-0,026) tiene silueta negativa y, con Chamberí (0,128, positiva pero baja), cambia de grupo con Ward. Los otros 19 distritos coinciden tras alinear las etiquetas (ARI entre métodos = 0,692). Moncloa-Aravaca, que en la versión anterior tenía silueta negativa, ya encaja en el grupo acomodado (0,148). Son casos para revisar, no motivos para borrar observaciones ni retocar k hasta que parezca mejor.

### Reutilizar resultados sin copiar etiquetas a mano

La siguiente celda prepara dos tablas en memoria: una fila por distrito con su asignación y diagnóstico, y los perfiles medios en valores reales. La exportación es opcional: por defecto **no crea archivos ni cambia las entradas**. Para reutilizarlos en un mapa o en la memoria, cambia `exportar` a `True`; se guardarán en `resultados_clustering/` dentro de la carpeta del caso. Las etiquetas de grupo solo sirven para esta ejecución y no deben interpretarse como un orden de gravedad.

## 8. Limitaciones y siguientes pasos

**Limitaciones (resumen de lo ya dicho):**

- Baseline exploratorio con separación modesta (silueta ~0,27); k = 3 es candidato provisional, no validado.
- En las pruebas realizadas, con escalado fijo, se mantienen las asignaciones comparables al quitar Centro, quitar los distritos imputados y cambiar la semilla, pero depende de los ejes económico y de edad, que llevan 5 celdas imputadas (estimaciones, no observaciones).
- La tabla mezcla todos los tipos de emergencia (ya con el criterio del catálogo aplicado en la limpieza); no hay segmentación por tipo.
- La oferta está incompleta (VALLECAS ambiguo, camas sin dato) y las bases catalogadas no miden cobertura real: no hay ninguna conclusión operacional.
- Es un modelo descriptivo, no predictivo: no dice qué pasará, solo cómo se parecen los distritos hoy. No se ha medido ningún ahorro.

**Continuación completada:** el notebook final incluye comparación de k, Ward, DBSCAN, sensibilidad, diagnóstico de edad y análisis socioeconómico. Este archivo conserva el baseline 10D como histórico.

## Recorrido exploratorio: preguntas, interpretación y límites

Registro del recorrido histórico integrado en el notebook socioeconómico. Las afirmaciones de provisionalidad describen esa fase; la selección vigente es 9D, con comparación 10D y contrapartidas explícitas en el cierre.

# Exploración de activaciones y distritos (caso 1.3): gráficos y mapas

Análisis exploratorio de los datos limpios del caso 1.3, pensado para la presentación intermedia: de aquí salen los números y los gráficos para contar el problema (qué pasa con las emergencias en Madrid), el volumen de datos y las primeras cosas que vemos al cruzar la demanda del SAMUR con el perfil social de los distritos.

La sección de exploración integrada reúne todo el análisis gráfico: los 12 gráficos de las secciones 1 a 9 y los 3 mapas de la sección 10. Cada gráfico lleva su explicación: qué se pregunta, qué se ve y qué no se puede concluir. La sección 11 resume los insights para los slides y la 12 recoge las limitaciones.

- **Datos usados:** `activaciones_limpio.csv` (146.567 activaciones del SAMUR en 2024, ya limpio en `data_clean/`, con el tipo y la prioridad del catálogo aplicados), `tabla_distritos.csv` (21 distritos con perfil social, demanda y oferta, en `1_3_clustering/`) y `tipos_emergencia_clean.csv` (catálogo canónico de tipos del caso 2.2, en `data_clean/`; la sección 4 solo añade la categoría, porque el tipo ya viene cruzado de la limpieza). Para los mapas, además, los límites oficiales de los distritos del Ayuntamiento de Madrid (se descargan al ejecutar).
- **Qué hace:** solo explorar y visualizar. No modifica ningún CSV ni rehace la limpieza.
- **Gráficos:** cada uno se guarda como PNG en la subcarpeta `graficos_eda/`, listo para meter en los slides.
- **Ojo al interpretar:** son 21 distritos y las correlaciones entre distritos no prueban causalidad. Los mapas son descriptivos: los terciles del mapa bivariante no son el clustering. Las dudas concretas están apuntadas al final (sección "Limitaciones").

**Nota de versión17/11:** exploración histórica. Las decisiones finales, correcciones hospitalarias, exclusión definitiva de oferta, pruebas de algoritmo y límites actualizados están documentados y ejecutados en `1_3_clustering/segmentacion_final_distritos.ipynb`; no se interpretan las cifras de camas del catálogo como capacidad comparable. No se asignan unidades ambiguas ni se usa hospital receptor para localizar avisos.

## 0. Carga de datos

Leemos los CSV ya limpios (los que salen de los notebooks de limpieza y de cruces), para que todo lo que se vea aquí sea reproducible desde el repo. Si el notebook está en `data_viz/`, las rutas relativas llegan solas; si no, se prueban otras ubicaciones típicas.

Decisión: para los análisis por hora usamos `hora_solicitud` (cuándo pide ayuda la gente, que es lo que interesa para planificar). Las 1.579 filas sin hora de solicitud se excluyen solo de esos gráficos, no del resto.

## 1. El volumen: más de 150.000 activaciones en un año

La presentación pide que se entienda el volumen de datos, así que empezamos por ahí. Contamos activaciones por mes para ver si la demanda es estable o tiene temporadas.

Decisión: como 2024 es bisiesto, el dato por día se calcula sobre 366 días.

**Lo que vemos:** unas **400 activaciones al día** de media (146.567 entre 366 días). Comparando por día (los meses no tienen los mismos días), junio es el mes con más actividad (438/día) y agosto el de menos (338/día, un 23% menos que junio). La lectura de que en agosto Madrid se vacía es una hipótesis razonable, no algo que el dato pruebe por sí solo. La demanda no es plana, así que tiene sentido estudiar cuándo hacen falta más recursos.

## 2. A qué hora pasan las cosas

Para planificar turnos importa la hora del día. Contamos activaciones por hora de solicitud y cruzamos mes × hora para comprobar si el patrón diario se mantiene todo el año o cambia con la temporada.

**Lo que vemos:** la demanda baja de madrugada (mínimo sobre las 4-5h) y sube hasta el mediodía, con el pico a las **13h** (casi 10.000 activaciones en el año, 3,3 veces más que a las 4h). El mapa de calor (normalizado por días de cada mes para que sean comparables) muestra un patrón diario parecido en todos los meses: no es cosa de un mes concreto.

## 3. La noche es otra emergencia

De día manda la patología cardiovascular; de madrugada, el ocio. Para verlo, calculamos qué porcentaje de las llamadas de cada hora son por intoxicación etílica.

**Límite de interpretación:** ocio es una hipótesis. Se miden horarios y tipos registrados; no se observa el motivo de presencia, la residencia ni la causa de esa distribución.


Decisión: mostramos el porcentaje dentro de cada hora (no el total), porque de madrugada hay menos llamadas en total y el volumen bruto escondería el efecto. Limitación: el dato abierto no trae el día de la semana, así que no podemos separar fin de semana de laborable (Bluetab lo confirmó por correo).

**Fuente y alcance:** fuentes primarias recuperadas en la sección de trazabilidad de correos. Las ventanas horarias, no imputar Vallecas y los valores del catálogo limpio siguen siendo decisiones propias, no una aprobación atribuible al remitente.


**Lo que vemos:** entre las 0 y las 7h la intoxicación etílica es el **tipo de emergencia nº1**, y a las 3 de la mañana es el **31%** de todas las llamadas (a mediodía no llega al 3%). Es el mismo servicio, pero dos realidades distintas según la hora, y eso importa para decidir qué recursos hacen falta en cada turno.

## 4. Categorías del catálogo de tipos (cohesión con el caso 2.2)

Desde la última versión de la limpieza de activaciones, `tipo_emergencia` **ya es** el código del catálogo canónico (`tipos_emergencia_clean.csv`, 39 tipos): la limpieza resolvió los alias y eliminó las filas cuyo tipo no describía una urgencia, así que el 100% de las activaciones tiene tipo catalogado. Aquí solo añadimos la **categoría** de cada tipo con un `merge` directo, para ver el reparto general del servicio.

Nota de cohesión: la prioridad que traen ahora las activaciones es la del catálogo (lo grave que suele ser cada tipo), no la registrada en cada evento; la del registro solo coincidía con ella en el 37,7% de las filas. El detalle está en `limpieza_activaciones.ipynb` (sección "Criterio del catálogo").

**Lo que vemos:** con las categorías del catálogo, **trauma (59.993, 40,9%) y patología médica (44.424, 30,3%) concentran más de 2 de cada 3 activaciones** del año; las intoxicaciones pesan un 11,0%. Esto conecta directo con el clustering: el "para qué" de la demanda de cada distrito se puede perfilar con estas categorías.

Ya no queda nada fuera del catálogo: la limpieza resolvió los alias (597 filas de abreviaturas y 1.564 de equivalencias clínicas, documentadas en `limpieza_activaciones.ipynb`) y eliminó 5.513 filas (el 3,6%) cuyo `tipo_emergencia` no describía una urgencia (recursos enviados, procedencia del aviso, servicios no asistenciales o lugar).

## 5. Qué tipo de emergencias y con qué prioridad

Para contar "el problema" hace falta decir qué atiende el SAMUR. Mostramos los 10 tipos más frecuentes y el reparto por prioridad (alta/media/baja, la que el catálogo asigna a cada tipo, con el criterio unificado que confirmó Bluetab). Los tipos ya vienen con el código canónico del catálogo desde la limpieza.

**Lo que vemos:** patología cardiovascular (28.715) y caídas (26.265) concentran más de un tercio del servicio. El **40% de las activaciones son de tipos de prioridad alta** según el catálogo. Ojo: antes este porcentaje medía la prioridad registrada en cada evento; ahora mide la gravedad típica del tipo, que es lo que deja la limpieza (las dos solo coincidían en el 37,7% de las filas).

Decisión: los tipos se muestran con el código literal del catálogo, que es como vienen en `activaciones_limpio.csv` desde la última limpieza.

Un detalle que no esperábamos: la mediana del tiempo de respuesta apenas cambia con la prioridad del tipo (7,0 min en alta, 7,1 en media y 7,6 en baja). El tiempo mide desde la solicitud hasta la intervención, así que no vemos si las urgentes se cuelan antes en la cola; no permite inferir priorización clínica ni orden de atención: esa conclusión queda fuera del alcance.

## 6. Edad y sexo registrados: diagnóstico, no interpretación clínica

La edad registrada tiene un reparto casi uniforme entre 0 y 99 años. Esto no demuestra su causa ni autoriza a llamarla sintética. Decisión cerrada: conservar valores y declarar el patrón; no usar edad ni sexo registrados para insights clínicos o demográficos. El porcentaje de mayores de 65 del socioeconómico es otra fuente y describe residentes, no pacientes. El notebook final documenta aparte el efecto de la edad registrada en la segmentación.

El gráfico y los conteos muestran un reparto casi uniforme de edad y sexos registrados próximos al 50/50. La causa no se puede determinar con el archivo disponible. No se interpreta como población real de pacientes ni se extraen conclusiones clínicas.

## 7. Dónde: la demanda no se reparte igual

Cruzamos con `tabla_distritos.csv`. Para comparar distritos de distinto tamaño usamos **activaciones por 1.000 residentes** (activaciones por población residente) (decisión ya tomada en los cruces: si no, los distritos grandes parecerían peores solo por tener más gente).

Centro es un caso aparte: 141 activaciones por 1.000 residentes, 3,1 veces la media simple de los 21 distritos (45) y 2,2 veces el segundo distrito (Moncloa-Aravaca, 65). Miramos si su perfil de activaciones apunta a una explicación.

Centro concentra el **24% de sus activaciones entre las 0 y las 7h** (en el resto de la ciudad, el 15%) y una vez y media las intoxicaciones etílicas (14% vs 9%). La hipótesis es clara: su demanda la dispara el ocio nocturno y la afluencia de gente que no vive ahí, no solo sus vecinos.

Ojo con el denominador: la población es de **residentes**, pero la activación ocurre donde está la persona en ese momento. En Centro buena parte de la demanda será de gente de paso (ocio, turismo, trabajo), no de vecinos, así que su ratio no se puede leer como "riesgo del vecino". En distritos más residenciales la lectura es más limpia.

¿Y la renta? En estos 21 distritos **no se ve** la relación del tópico "más vulnerabilidad, más emergencias": la correlación entre activaciones por población residente y renta media sale positiva (0,19 con Centro, 0,41 dejándolo fuera; damos los dos números porque un solo distrito mueve mucho el resultado). No es una ley general: es lo que muestran estos datos. Una lectura plausible es que los distritos con más renta son también los más envejecidos según el censo (Salamanca, Chamartín), y las activaciones por población residente también suben con el % de mayores de 65 del distrito (0,38 sin Centro). No lo podemos confirmar con la edad del paciente, que presenta un patrón de registro anómalo y no usamos como evidencia demográfica. Aun así, son 21 puntos y una correlación: lo tratamos como hipótesis para el clustering, no como conclusión.

## 8. El tiempo de respuesta: la densidad manda

**Lectura vigente:** rótulo histórico. Solo se demuestra una asociación descriptiva o una comparación de catálogos, no que la densidad cause los tiempos ni que la red tenga una eficacia o cobertura verificadas.


La otra cara del servicio: cuánto se tarda en llegar. Usamos `tiempo_de_respuesta` (solicitud → intervención, con la regla de medianoche aplicada en la limpieza; antes se llamaba `tiempo_respuesta_min`).

**Lo que vemos:** la mitad de las activaciones se atiende en **7 minutos o menos** (el 60% en 8), pero la diferencia entre distritos es grande: de 6,5 min en Chamberí a 10,7 min en Barajas. La correlación entre densidad y tiempo medio de respuesta es **-0,87**, la asociación más fuerte de todo el análisis. Es una correlación entre medias de 21 distritos, no una prueba causal; la lectura plausible (en distritos densos las unidades están físicamente más cerca) es una hipótesis. Los distritos dispersos de la periferia (Barajas, Villa de Vallecas, Vicálvaro, Fuencarral) son los que más esperan, y ahí el cuello de botella parece geográfico, no de volumen.

Como hipótesis de trabajo es sólida y va directa al objetivo del proyecto (dónde hacen falta recursos).

## 9. Oferta y demanda: la red funciona como red

**Lectura vigente:** rótulo histórico. Solo se demuestra una asociación descriptiva o una comparación de catálogos, no que la densidad cause los tiempos ni que la red tenga una eficacia o cobertura verificadas.


Último cruce: ¿los distritos con más recursos son los de más demanda? Comparando unidades SAMUR con base en cada distrito frente a su demanda por habitante.

Aquí el dato clave, con el denominador claro: de las 113.905 activaciones con unidad y distrito identificados (el 78% del total; fuera quedan 601 sin distrito asignable y 32.061 atendidas por unidades cuya base no tiene distrito seguro), **solo el 5,8% las atiende una unidad con base en el mismo distrito de la activación**. Y mirando solo los 7 distritos que tienen unidades con base propia (51.156 activaciones identificadas), el porcentaje sube solo al 13%. Es decir: la base registrada no dice dónde trabaja cada unidad, y los datos encajan con una gestión en red de la ciudad (el dato no dice qué zona cubre cada unidad). En esa línea, distritos sin base propia (como Chamberí) tienen tiempos de respuesta buenos.

Dos matices honestos: que la base de la unidad esté en otro distrito no significa que la unidad no cubra esa zona (los recorridos no están en el dato), y 32.061 activaciones (22%) las atienden unidades cuya base no se puede asignar a un distrito: 10 unidades del catálogo tienen la base `VALLECAS` a secas, que no distingue Puente de Villa de Vallecas, y 5 la tienen `NO CONSTA` o vacía. Por eso Puente y Villa de Vallecas no salen en el gráfico: sus unidades son desconocidas, no 0.

## 10. Mapas de distritos: actividad, tiempo de respuesta y contexto social

Hasta aquí hemos visto los distritos en gráficos de barras y de puntos. Los mapas responden a una pregunta que esos gráficos no enseñan bien: **dónde está cada cosa en Madrid**. Son tres, y cada uno se apoya en el anterior:

1. **Actividad frente a tiempo de respuesta** (dos mapas lado a lado): dónde se concentran las activaciones y dónde tarda más la respuesta.
2. **Mapa bivariante:** las dos variables juntas, para ver qué distritos combinan actividad alta o baja con respuesta rápida o lenta.
3. **Contexto social:** renta, vulnerabilidad y población mayor de 65, como marco para el clustering.

Usan solo la tabla por distrito del proyecto (`tabla_distritos.csv`, 21 filas, ya cargada arriba como `tabla`). No repiten la limpieza ni usan puntos por emergencia: el dato abierto no trae la ubicación exacta.

### 10.1 Datos y límites oficiales

Los límites de distrito vienen del servicio de mapas oficial del Ayuntamiento de Madrid (capa DISTRITOS, ETRS89 / UTM 30N, término municipal, no Comunidad). Se descargan al ejecutar, no se dibujan a mano. Se une por el código de distrito (1 a 21) y no por el nombre, porque los nombres se escriben distinto según la fuente (decisión coherente con los problemas de nombres que ya vimos en la limpieza).

Decisión: antes de dibujar los mapas restablecemos el estilo de matplotlib a los valores por defecto, porque el estilo de las secciones anteriores (cuadrícula, tamaño de letra) está pensado para gráficos de ejes y estropea los mapas.

### 10.2 Comprobaciones antes de dibujar

Los 21 códigos coinciden y la superficie del polígono oficial es parecida a la de la tabla. Si algo no encajara, el `assert` de arriba pararía el notebook en vez de dibujar un mapa con distritos mal unidos.

### 10.3 Mapa 1: actividad y tiempo de respuesta, lado a lado

**Pregunta:** ¿dónde se concentra la actividad del SAMUR y dónde tarda más la respuesta?

**Cómo está hecho:** activaciones por 1.000 residentes (mapa izquierdo) y tiempo medio de respuesta en minutos (mapa derecho), cada uno con su escala y su rango real (mínimo y máximo en la leyenda). Los distritos centrales son pequeños, así que sus etiquetas van aparte, unidas con una línea.

**Cómo leerlo:** cuanto más oscuro, mayor valor. Los dos mapas tienen escalas distintas y no se comparan color con color: se comparan posiciones.

**Qué vemos:** Centro destaca mucho en actividad (141 activaciones por 1.000 residentes, 3,5 veces la media simple de los otros 20 distritos, que es 41; después viene Moncloa-Aravaca con 65). En tiempo de respuesta pasa casi lo contrario: los más lentos están en el borde del municipio (Barajas 10,7 min, Villa de Vallecas 10,0, Vicálvaro 9,8) y el más rápido es Chamberí (6,5).

**Qué no dice:** la activación se cuenta en el distrito donde ocurre, no donde vive el paciente, y la población es de residentes. En Centro y Barajas la población presente no está medida, y eso puede afectar a la interpretación de la ratio (es una hipótesis sobre visitantes, no algo medido). El denominador de "3,5 veces" es la media simple de los otros 20 distritos; en la sección 7 la comparación era con los 21 (3,1 veces): mismo dato, distinto denominador. Un tiempo de respuesta largo tampoco demuestra falta de cobertura.

**Para qué sirve en el proyecto:** plantea las dos variables que tiene que capturar el clustering (demanda por habitante y tiempo de respuesta) y enseña que no van siempre juntas.

### 10.4 Mapa 2: bivariante (actividad y tiempo de respuesta juntos)

**Pregunta:** si cruzamos las dos variables, ¿qué tipos de distrito aparecen?

**Cómo está hecho:** cada variable se divide en terciles (tres grupos de 7 distritos: bajo, medio, alto) y se combinan en una paleta de 3×3. Es una clasificación para visualizar, **no es un modelo de clustering**.

**Cómo leerlo:** el eje horizontal de la leyenda es la actividad por 1.000 residentes y el vertical, la lentitud de la respuesta. El título del mapa y el recuadro de la derecha dicen qué distritos caen en cada esquina.

**Qué vemos:** más actividad por habitante suele ir con respuesta media más rápida (Spearman -0,60, n = 21). Alta actividad y respuesta rápida: Centro, Arganzuela, Salamanca, Tetuán y Chamberí. Baja actividad y respuesta lenta: Fuencarral-El Pardo, Hortaleza, Villaverde, Villa de Vallecas y Vicálvaro. Alta actividad con respuesta lenta solo aparece en Barajas. El tiempo de respuesta se asocia todavía más con la densidad (Spearman -0,88).

**Qué no dice:** con 21 distritos la correlación es orientativa y no es causal. Los terciles dependen de dónde se ponga el corte (un distrito cerca del límite podría cambiar de grupo). Aquí la correlación es de Spearman (por rangos); en la sección 8 usamos Pearson (-0,87 entre densidad y tiempo): son dos medidas distintas de lo mismo y las dos apuntan a lo mismo. No mide cobertura, porque no tenemos la ubicación exacta de las unidades.

**Para qué sirve en el proyecto:** da una primera clasificación a mano con la que comparar después el resultado del k-means y del jerárquico: si el clustering encuentra algo distinto, tendremos que explicar por qué.

### 10.5 Mapa 3: contexto social

**Pregunta:** ¿cómo son socialmente los distritos que acabamos de ver?

**Cómo está hecho:** tres mapas con la renta media del hogar, el índice de vulnerabilidad (0 a 1) y el porcentaje de población mayor de 65 años. Los **6 valores marcados con \*** están imputados: en los datos originales faltaban 10 huecos y se rellenaron con la media de los 3 distritos más parecidos (como indica el README del proyecto); solo 6 de ellos se ven en estos mapas.

**Cómo leerlo:** cada mapa tiene su propia escala y su rango real en la leyenda (por ejemplo, mayores de 65: de 11,2 % a 26,8 %).

**Qué vemos:** el sur (Villaverde, Usera, Vallecas, Latina) reúne menos renta y más vulnerabilidad; Salamanca, Chamartín, Retiro y Chamberí combinan más renta y más población mayor.

**Qué no dice:** no explica las activaciones. En la sección 7 ya vimos que en estos 21 distritos no aparece la relación "más vulnerabilidad, más emergencias", y estos mapas no la contradicen ni la demuestran. Los valores con * son estimaciones metodológicas, no datos observados; su sensibilidad se mide en el cierre.

**Para qué sirve en el proyecto:** es el marco de las variables sociales del clustering y permite imaginar qué perfiles de distrito vamos a comparar.

## 11. Resumen para los slides

| # | Insight | Cifra clave | Gráfico |
|---|---------|-------------|---------|
| 1 | El SAMUR no para: volumen diario enorme | 146.567 activaciones en 2024; 400 al día de media (146.567 / 366 días, promedio calculado, no una serie diaria observada) | `activaciones_por_mes.png` |
| 2 | La demanda cambia con el mes | por día: junio 438, agosto 338 (-23% respecto a junio) | `activaciones_por_mes.png` |
| 3 | El día tiene un ritmo parecido todos los meses | pico a las 13h, 3,3x el valle de las 4h | `activaciones_por_hora.png`, `heatmap_mes_hora.png` |
| 4 | La noche es otra emergencia | a las 3h, el 31% de las activaciones es por intoxicación etílica (a mediodía no llega al 3%); de 0 a 7h es el tipo nº1 | `intoxicacion_nocturna.png` |
| 5 | Qué se atiende | cardiovascular y caídas = más de 1/3 del servicio; 40% de tipos de prioridad alta (catálogo) | `tipos_emergencia_top10.png`, `prioridades.png` |
| 6 | La edad y el sexo publicados tienen un patrón no interpretable clínicamente | reparto casi uniforme 0-99 y sexos próximos al50/50; causa no determinada, sin interpretación clínica | `edad_pacientes.png` |
| 7 | Centro es otro mundo | 141 act./1.000 residentes, 3,1x la media de distritos (2,2x el segundo); 24% de su demanda es de madrugada | `demanda_por_distrito.png` |
| 8 | En estos 21 distritos no se ve "más vulnerabilidad, más emergencias" | corr. renta-activaciones/residente +0,19 (+0,41 sin Centro); suben con el % de mayores del censo | `renta_vs_demanda.png` |
| 9 | Los distritos densos tienen respuesta más rápida | corr. -0,87 entre medias distritales (n=21); de 6,5 min (Chamberí) a 10,7 min (Barajas) | `densidad_vs_tiempo_respuesta.png` |
| 10 | Base de la unidad y distrito de la activación casi nunca coinciden | 5,8% de las identificadas (13% en los 7 distritos con base propia) | `oferta_vs_demanda.png` |
| 11 | Trauma y patología médica son 2 de cada 3 activaciones | 40,9% + 30,3% (categoría del catálogo canónico; el 100% de las activaciones ya trae tipo catalogado de la limpieza) | `activaciones_por_categoria.png` |
| 12 | Mapa: mucha actividad en el centro, respuestas más lentas en la periferia | Centro 141 act./1.000 residentes (3,5x la media simple de los otros 20 distritos, 41); Barajas 10,7 min, Villa de Vallecas 10,0, Vicálvaro 9,8 frente a 6,5 en Chamberí | `mapa_demanda_vs_respuesta.png` |
| 13 | Mapa bivariante: más actividad por habitante suele ir con respuesta más rápida | Spearman -0,60 (actividad vs tiempo) y -0,88 (densidad vs tiempo), n = 21; solo Barajas combina actividad alta y respuesta lenta. Terciles descriptivos, no clustering | `mapa_bivariante_demanda_respuesta.png` |
| 14 | Mapa social: el sur tiene menos renta y más vulnerabilidad | Villaverde, Usera, Vallecas y Latina frente a Salamanca, Chamartín, Retiro y Chamberí (más renta, más mayores). Marco del clustering, no explicación; 6 valores imputados marcados con * | `mapa_contexto_social.png` |

Conexión con el caso 1.3: los insights 7-9 y los tres mapas (12-14) son exactamente lo que el clustering tiene que capturar: distritos con perfiles de demanda y respuesta muy distintos, que piden estrategias distintas.

## 12. Limitaciones (para no vender de más)

- **Correlación ≠ causalidad**, y con 21 distritos cualquier correlación es frágil. Los insights 8 y 9 son hipótesis buenas para el clustering, no conclusiones cerradas.
- **Sin día de la semana:** el dato abierto solo trae año, mes y hora (confirmado por Bluetab). No podemos separar fin de semana de laborable ni cruzar con meteo o calendario.
- **La oferta es de catálogo y puede estar incompleta:** contar hospitales o bases no mide la cobertura real, y un distrito sin registros se contó como 0.
- **Datos imputados:** 10 huecos del socioeconómico se imputaron con los 3 distritos más parecidos (kNN) y están marcados como imputados en la tabla.
- **Edad y sexo del paciente:** el reparto es prácticamente uniforme (0-99, 50/50), su causa no se puede determinar con estos datos: patrón no interpretable clínicamente con estos datos; decisión definitiva: no usarlos para insights demográficos.
- **Lugar de activación ≠ residencia:** la demanda por 1.000 habitantes usa población residente, pero la gente se mueve; en Centro (ocio, turismo) el ratio mezcla demanda de visitantes con población vecina.
- **Prioridad y tipos son del catálogo:** desde la última limpieza, `tipo_emergencia` es el código del catálogo (39 tipos) y `prioridad` la gravedad típica que el catálogo asigna al tipo; la prioridad registrada en cada evento ya no está en el CSV (solo coincidía con la del catálogo en el 37,7% de las filas). Las filas cuyo tipo no describía una urgencia (5.513, el 3,6%) se eliminaron en la limpieza y no entran en estos gráficos. El script que genera el catálogo (`limpieza_tipos_emergencia.py`) cita un "anexo" como fuente de sus valores corregidos y ese documento no está en el repo; además el script sigue generando el catálogo antiguo de 42 tipos, no el de 39 que usa la limpieza (versión histórica; el cierre usa y comprueba el catálogo limpio de 39 códigos).
- **Catálogo de unidades sin zona de cobertura:** los `unidad_id` encajan al 100% con el catálogo, pero el catálogo no dice qué zona cubre cada unidad (base ≠ zona de cobertura).
- **Distritos sin asignar:** 601 activaciones (0,4%) sin distrito de Madrid ciudad (NO CONSTA, fuera de término y carreteras; sin afirmar cuántas de las 39 etiquetas VALLECAS de origen sobreviven a filtros) quedan fuera del análisis por distrito.
- **Años:** las activaciones son de 2024 y el socioeconómico usa población de 2024; otros indicadores pueden ser de otra ola.
- **Mapas (sección 10):** son descriptivos. Los terciles del mapa bivariante dependen del corte y no son clustering. El denominador es población residente, no población presente (en Centro y Barajas no está medida). El tiempo de respuesta medio no es cobertura ni calidad del servicio. No hay ubicación exacta de las emergencias, por eso no hay puntos en los mapas. En el mapa social, 6 valores visibles son imputados (marcados con *).
- **Dos denominadores para Centro:** 3,1 veces la media simple de los 21 distritos (sección 7) y 3,5 veces la media simple de los otros 20 (mapa 1): mismo dato, distinto denominador, y en cada sitio se dice cuál es.

## Consolidación final solicitada el 17/11/2026

Se conserva cruces como notebook independiente. El otro notebook incorpora todas las 24 celdas del baseline y las 44 de la exploración socioeconómica previa, además de todas las pruebas y análisis del cierre. Los ajustes de integración son rutas de lectura/escritura y rótulos; no se cambia ningún algoritmo para mejorar métricas. Las tablas y los JSON de resultados se comparan con el cierre anterior y coinciden byte a byte.

La secuencia narrativa separa deliberadamente recorrido histórico y conclusión vigente. Que el baseline llame provisional a k=3 o no utilice todavía análisis por tipo describe esa fase; las pruebas adicionales y el análisis por tipos vienen después en el mismo notebook. Los anteriores README_cierre y README_recursos se absorben aquí y se conservan en archivo; no hay que leerlos como guías vigentes.

Al aplicar esta estructura en la rama, los únicos notebooks activos de 1_3_clustering deben ser cruces_datasets.ipynb y segmentacion_final_distritos.ipynb. Las versiones anteriores clustering_distritos.ipynb, main.ipynb y los dos README secundarios quedan en archivo, no se pierden. Las limpiezas compartidas y el EDA original fuera de esta carpeta no se mueven ni se eliminan. Las salidas intermedias, JSON y gráficos son dependencias o evidencias, no finales alternativos.


## Verificación de atribuciones y lectura prudente del histórico


### Trazabilidad de los correos citados y alcance real

Se releyeron las fuentes primarias de la cuenta UC3M el 17/11/2026. El mensaje recibido de `cruz.mateo@bluetab.net`, del 14/10/2026 a las 12:07 CEST, asunto de seguimiento del proyecto, ID `1a139e1c233cd6d2`, respalda la ausencia de día, las equivalencias de prioridad, el rango 0-115 y la distinción de variantes explícitas de Vallecas frente a los 39 registros ambiguos de origen. Describe mismo día salvo cruce de medianoche, pero NO fija nuestras ventanas 20:00-23:59 y 00:00-06:59: esas ventanas y su cuantificación son decisión propia basada en la distribución observada. El mensaje permite más de una solución para Vallecas; elegimos no imputar, con el motivo explicado aquí. No convierte la cifra de origen en un recuento final.

El mismo correo exige un criterio consistente para corregir el catálogo, pero NO aprueba cada equivalencia clínica, categoría, prioridad ni tiempo elegido después. Esas decisiones son nuestras y se justifican en la limpieza. El mensaje de `david.millan@bluetab.net`, 14/10/2026 a las 12:21, ID `1a139eeab43196b9`, solicita propuestas y justificación, no es aprobación de una solución concreta.

**Fuente y alcance:** fuentes primarias recuperadas en la sección de trazabilidad de correos. Las ventanas horarias, no imputar Vallecas y los valores del catálogo limpio siguen siendo decisiones propias, no una aprobación atribuible al remitente.


El mensaje recibido de `maria.angeles.quesada@bluetab.net`, 15/09/2026 a las 17:55 CEST, ID `1a0a5c9f014196b8`, comunica el envío del dataset y planteamiento del proyecto. Esto respalda la fecha de entrega, NO el año de observación de cada catálogo ni una supuesta instantánea homogénea de 2024.

Las anotaciones históricas que atribuyen al cliente la prohibición de diccionarios cerrados no tienen aquí una fuente primaria concreta recuperada. Se conservan como anotación histórica no verificada; no se usan como autoridad metodológica. La regla de normalización se defiende por ser explícita, reproducible y no forzar equivalencias ambiguas.


### Correcciones de interpretación junto al recorrido histórico


## 3. Composición por hora: intoxicación etílica

En el recorrido histórico se describió la madrugada en términos de ocio. La medición real aquí es el porcentaje de activaciones de cada hora por intoxicación etílica. Ese porcentaje permite comparar composición entre horas, no observar la actividad que causó la emergencia ni probar que se deba a ocio.

Se muestra porcentaje dentro de cada hora, porque de madrugada hay menos activaciones y un conteo bruto respondería otra pregunta. No se dispone de día de semana, por lo que no se separan fines de semana y laborables. Esa ausencia de día está respaldada por el correo primario del 14/10 identificado en la trazabilidad de la sección A.

**Fuente y alcance:** fuentes primarias recuperadas en la sección de trazabilidad de correos. Las ventanas horarias, no imputar Vallecas y los valores del catálogo limpio siguen siendo decisiones propias, no una aprobación atribuible al remitente.


Centro concentra el 24% de sus activaciones entre las 0 y las 7 h, frente al 15% en el resto de la ciudad, y una proporción mayor de intoxicaciones etílicas (14% frente a 9%). La explicación por ocio nocturno o afluencia de no residentes es una hipótesis, no una causa observada: no tenemos itinerarios, motivo de presencia ni residencia del paciente.

El denominador es población residente y el numerador es actividad localizada en el distrito. Por eso la tasa no mide riesgo de sus vecinos. No se puede cuantificar qué parte pertenece a visitantes con estas tablas ni afirmar que esa parte sea mayoritaria. Se conserva la hipótesis histórica como posible interpretación, separada del dato medido.

## 8. Tiempo de respuesta y densidad: asociación distrital

El rótulo histórico atribuía un papel determinante a la densidad. Aquí se mide asociación entre medias de distrito, no un efecto causal. Se explora la distribución de tiempos y su relación con densidad, manteniendo todos los límites del dato.

La mediana global del tiempo válido es 7,2 minutos y el 60% de las activaciones con tiempo válido está en 8 minutos o menos. Los tiempos medios distritales van de 6,5 minutos en Chamberí a 10,7 en Barajas. Densidad y tiempo medio presentan Pearson r = -0,87 en 21 distritos.

Es una asociación descriptiva fuerte entre esas dos variables, no la mayor correlación de todo el proyecto ni una prueba causal. La explicación por distancia, proximidad de unidades o geografía sigue siendo una hipótesis. No hay localización exacta de salida, trayecto ni medición de cobertura que permita identificar un cuello de botella. La mediana y el P90 con casos válidos y faltantes se desarrollan después en la sección final.

## 9. Oferta de catálogo y demanda: descripción, no prueba de cobertura

Se compara el distrito de base catalogado de las unidades con demanda por habitante. El rótulo histórico sugería funcionamiento de una red; esa eficacia o cobertura NO queda demostrada por contar bases o por la coincidencia entre base y lugar de activación. Las unidades se pueden desplazar, pero este catálogo no permite reconstruir su operación.

Se conservan todos los cálculos de la exploración y se interpretan como descripción de catálogos, con unidades ambiguas sin asignar y sin completar oferta desconocida.

Estos matices no cambian los conteos, las tablas ni los modelos. Corrigen el alcance de la interpretación. Las formulaciones originales se conservan íntegras en el archivo de fuentes; no se borran como si nunca hubieran existido.