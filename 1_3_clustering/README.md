# Caso 1.3 - Segmentación socio-sanitaria de Madrid

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
- **Edad:** se mantienen los valores entre 0 y 115 años; las edades fuera de ese rango pasan a nulo, sin borrar la fila ni sustituirlas por una media. Bluetab confirmó por correo (14/10) que 0-115 es válido y que se acepta cualquier límite razonable y justificado; lo que no se acepta es dejar edades negativas o imposibles sin tratar.
- **Datos que faltan:** en hospital, sexo y distrito usamos `NO CONSTA`. En hospital no usamos `SIN TRASLADO`, porque que el campo esté vacío no demuestra que no hubiera traslado. En tipo de emergencia y prioridad también se usa en la primera pasada, pero esas dos columnas acaban tomando el valor del catálogo, así que en el CSV final no queda ningún `NO CONSTA` en ellas.
- **Hospital 12 de Octubre:** nombre unificado como `HOSPITAL 12 DE OCTUBRE` para no mantener varias formas del mismo hospital.
- **Vallecas:** `VALLECAS PTE.`, `P. VALLECAS` y `PUENTE DE VALLECAS` se agrupan como Puente de Vallecas; `VILLA DE VALLECAS` se mantiene aparte. Bluetab confirmó por correo (14/10) que esas variantes son Puente y que el único valor ambiguo es `VALLECAS` a secas (39 filas), que podíamos excluir del análisis por distrito o asignar al distrito más frecuente, documentándolo. En la reunión del 15/10 comentaron que quizá se podía resolver con otros datasets. Lo probamos (ver abajo) y no se puede, así que esas 39 filas pasan a `NO CONSTA`.
- **Duplicados:** 737 copias idénticas eliminadas (de 152.844 a 152.107 filas). Si un `activacion_id` se repite con datos distintos, conservamos las filas porque no sabemos cuál es la correcta. Al unificar después los alias del catálogo aparecen 27 duplicados exactos más que antes eran invisibles porque el texto difería (una fila decía `PCR` y su pareja `PATOLOGIA CARDIOVASCULAR`); como los 27 pares comparten `activacion_id` y ya no se diferencian en nada, se eliminan con la misma regla. Quedan 25 `activacion_id` repetidos con contenido realmente distinto.
- **Cruces de medianoche:** 610 filas traían la intervención antes que la solicitud (616 antes de quitar duplicados, el número que también tenía Bluetab). Siguiendo su correo (14/10): asumimos que solicitud e intervención son del mismo día salvo cruce de medianoche, y nuestra regla es solicitud entre las 20:00 y las 23:59 e intervención entre las 00:00 y las 06:59, que suma 24 horas (569 filas). Las 41 que no encajan son errores de registro: el tiempo de respuesta queda vacío pero la activación se conserva. Los límites salen de los propios datos: el 92% de esas filas pide a las 23 horas y el 95% interviene a las 00, y con esos límites todas las duraciones resultantes son posibles según los tiempos del mismo día (la mayor es de unas 5 horas; los tiempos del mismo día llegan a 11). El detalle está en `limpieza_activaciones.ipynb`.
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

- **Unidades SAMUR:** miramos la base de la unidad que atendió cada activación. En el resto de distritos con base solo coincide con el distrito de la activación el 11% de las veces (más o menos una de cada ocho, como si fuera al azar), y las 39 filas se reparten entre las mismas bases que las de Puente y Villa. No sirve.
- **Hospital:** solo 15 de las 39 filas tienen hospital (9 Gregorio Marañón y 5 Infanta Leonor) y los dos hospitales reciben activaciones de Puente y de Villa. Da una probabilidad, no una certeza.
- **Accidentes, meteorología y calendario:** no comparten ninguna clave con esas filas.
- **Por qué no las asignamos a Puente (el más frecuente, 72%):** sería inventar el dato, porque seguro que una parte son de Villa. Son el 0,03% de las filas, así que dejarlas fuera del análisis por distrito casi no cambia nada, y siguen contando en la demanda total.

## Cruces entre datasets

`cruces_datasets.ipynb` revisa qué datasets se pueden cruzar y monta `tabla_distritos.csv`: una fila por distrito con perfil social, demanda y oferta sanitaria. Es la tabla que entra al clustering.

- **Socioeconómico + distritos:** encajan 21 de 21 por `distrito_id`.
- **Activaciones por distrito:** nº de activaciones, activaciones por 1.000 habitantes (para que los distritos grandes no parezcan peores solo por tener más gente), % de prioridad alta, edad media de los pacientes y tiempo medio de respuesta (ya con la regla de medianoche aplicada). Las 567 filas con distrito `NO CONSTA`, las 33 de fuera del término municipal y la de `CARRETERAS Y CIRCUNVALACIONES` cuentan en la demanda total, pero no se asignan a ningún distrito.
- **unidades_samur: sí.** Encaja el 100% por `unidad_id` (por id, no por código, que se repite). Da la carga por unidad y las unidades de cada distrito.
- **bases_samur y hospitales: sí.** Oferta por distrito: bases, unidades, hospitales y camas. Los catálogos escriben el distrito de otra forma (`LA LATINA`, `FUENCARRAL`, `VALLECAS`), así que se normaliza con una regla (quitar el artículo y completar si el texto es el principio de un único distrito oficial), sin diccionarios. Las unidades se buscan solo entre los distritos con base, y así `VALLECAS` encaja en Puente de Vallecas. Lo que no encaja (hospitales de otros municipios y el Hospital Infanta Leonor, cuyo distrito es solo `VALLECAS`) se lista y se deja fuera. Un distrito que no sale en un catálogo (sin base, sin unidades o sin hospital) cuenta 0 en esa columna, porque el catálogo no tiene registros suyos; es una suposición nuestra y así la tabla no tiene huecos. Un hospital que sí sale pero sin dato de camas (Fundación Jiménez Díaz, en Arganzuela) no se cuenta como 0 camas: se le pone la media de camas de los hospitales que sí tienen el dato (876).
- **Comprobación con `distritos.csv`:** `num_hospitales` no coincide con el catálogo de hospitales en 12 de 21 distritos, y `base_samur` no coincide con el catálogo de bases en 6 de 21. No corregimos ninguna de las dos fuentes y la tabla usa los catálogos.
- **Normalización 0-1:** igual que en el socioeconómico, las columnas numéricas de la tabla pasan a escala 0-1 con min-max y se guardan en `tabla_distritos_norm.csv`, que es la que entra al clustering. Como la oferta ya trae 0 donde no hay recursos, la tabla normalizada no tiene valores vacíos. Si una columna fuera constante (mismo valor en todos los distritos) se deja en 0, porque no distingue distritos y el min-max daría error.
- **tipos_emergencia: sí, ya resuelto.** Antes no se unía porque `INTOXICACION ETILICA` y `CAIDA` salían dos veces en el catálogo con categoría y prioridad distintas, y no había forma de saber cuál era la correcta. Eso se arregló en `limpieza_tipos_emergencia.py` (que deja una sola entrada de cada una) y en `limpieza_activaciones.ipynb`, donde se unifican los alias y se aplica el criterio del catálogo (ver "Criterio del catálogo"). Ahora `activaciones_limpio.csv` ya trae el tipo y la prioridad del catálogo, así que no hay que cruzar nada aquí: la columna `tipo_emergencia` es directamente `tipos_emergencia_clean.codigo`. Si se necesita la categoría, el tiempo objetivo o si requiere médico, se traen con un `merge` por esa columna.
- **accidentes: no para el clustering.** Es de tráfico, incluye municipios de fuera de Madrid y le faltan distritos. Posible ampliación (riesgo vial).
- **meteorología y calendario: no se puede.** Van por día y las activaciones no tienen día: el dato abierto del SAMUR solo publica año, mes y horas (Bluetab lo confirmó por correo el 14/10), así que no hay cruce por fecha. Es una limitación del dato, no algo que podamos inventar.
