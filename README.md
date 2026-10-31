# Project-UC3M

Casos de uso con datos de emergencias del SAMUR de Madrid (proyecto con Bluetab).

## Estructura

- data/            datos originales (no modificar)
- data_clean/      datasets limpios (`<dataset>_clean.csv`)
- cleaning/        scripts que pasan de data/ a data_clean/
- 1_1_volume/      Predicción de volumen de emergencias
- 1_2_severity/    Clasificación de gravedad en accidentes
- 1_3_clustering/  Segmentación socio-sanitaria
- 2_1_rag/         Agente RAG sobre informes de accidentes
- 2_2_triage/      Agente de clasificación de emergencias

## Instalación

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Las claves de API (si hacen falta) van en un fichero .env local.
Este fichero no se sube a GitHub.

## Reparto


| Caso | Responsable |
| ---- | ----------- |
| 1.1  | Bea         |
| 1.2  | Lukas       |
| 1.3  | Diego       |
| 2.1  | Dani        |
| 2.2  | Pablo       |




## Normas de trabajo

- Cada uno trabaja en su rama (ej. caso-2.2-limpieza).
- Nada entra en main sin pull request.
- Nunca subir claves ni el fichero .env.



## Accidentes — limpieza común (casos 1.2 y 2.1)

`data_viz/accidentes-analysis.ipynb` lee `data/accidentes.csv` y escribe `data_clean/accidentes_clean.csv` (1962 filas × 26 columnas, una por `numero_incidencia`). No modifica el original. Une las dos limpiezas que había (`1_2_severity/data_cleaning.ipynb` y `2_1_rag/pipeline.py`) y es la única entrada de `1_2_severity/feature_engineering.ipynb` y de `2_1_rag/embeddings.py`. El mismo notebook genera los gráficos de `data_viz/graficos_accidentes/`; `data_viz/diagrama_pipeline_accidentes.py` dibuja el diagrama del proceso (`00_pipeline_diagrama.png`).

Las dos limpiezas anteriores se conservan como referencia, pero sus salidas (`1_2_severity/data/accidentes_clean.csv` y `data/accidentes_clean.csv`) ya no las usa nadie.

### Decisiones de limpieza

**Duplicados.** 100 números de incidencia aparecen dos veces: es el mismo accidente. Se conserva la fila con más campos rellenos; si empatan, la de descripción más larga y, después, la anterior. Un `-1` cuenta como vacío. Si la fila conservada tiene un campo vacío y la descartada lo trae relleno, se copia ese valor (3 celdas). Las 45 discrepancias entre copias se registran.

**Se dejan como vienen.** `numero_incidencia`, `hora`, `localizacion`, `eje`, `descripcion` y `unidad_samur_id`. También `ubicacion` (`SUPERFICIE`, `TÚNEL`), `tipo_accidente` y `distrito`.

**Categóricas.** `(En blanco)`, `0`, `_` y el vacío pasan a nulo. El resto se unifica a una sola grafía: minúsculas, sin acentos ni puntuación. Si no hay un mapa, se usa la grafía más frecuente.

- `estado_firme`: `seco` y `seco y limpio` → `Seco y limpio`; `mojado` → `Mojado`; `humedo` → `Húmedo`. `Otros` se queda.
- `tipo_via`: `TRONCO`, `VIA DE SERVICIO`, `RAMAL`, `TRANSFER`, `TABLERO`, `TUNEL`.
- `carretera`: mayúsculas y sin guion. `M-607` y `M607` → `M607`. El vacío pasa a nulo.
- `tipo_colision`: de los 71 vacíos tras deduplicar, 68 se rellenan con el tipo que Claude infirió desde la descripción (`infer_tipo_colision` en `2_1_rag/pipeline.py`) y se marcan en `tipo_colision_inferido`. Los 3 sin descripción siguen vacíos. El notebook no llama a la API: lee `.cache/tipo_colision.json` y, si no existe (`.cache/` no se sube), los tipos que ya guarda `data_clean/accidentes_clean.csv`.
- `circulacion`: vacío, `0` y `_` → nulo. `FLUIDA`, `CONGESTIONADA` y `DENSA` se quedan.

**Recuentos.** Pasan a número. `-1` es un dato ausente y pasa a nulo (`vehiculos_implicados` y `heridos_leves`). Los 17 ceros de `vehiculos_implicados` se conservan. `motos_implicadas`, `pesados_implicados`, `heridos_graves` y `victimas_mortales` no traen `-1`.

**Columnas nuevas**

- `fecha`: se toma del `numero_incidencia` (`AAAAMMDD-…`), en formato `YYYY-MM-DD`. Corrige 42 fechas cuyo texto tenía día y mes invertidos o desplazados. `fecha_calendario` es la misma fecha como `datetime`.
- `hora_decimal`: la hora de `hora`, en horas + minutos/60 + segundos/3600.
- `grave`: 1 si `heridos_graves > 0` o `victimas_mortales > 0`. Un recuento ausente no cuenta como grave. Son 45 de 1962.
- `tipo_colision_inferido`: True en los 68 `tipo_colision` rellenados desde la descripción.
- `fuera_de_madrid`: True en los 50 partes de municipios vecinos (Móstoles, Alcorcón…).

## Caso 1.2 — Clasificación de gravedad



### Ingeniería de variables

`1_2_severity/feature_engineering.ipynb` lee `data_clean/accidentes_clean.csv`, construye las variables y después parte la tabla. Escribe `accidentes_train.csv`, `accidentes_test.csv` y `variable_dictionary.csv` en `1_2_severity/data/`.

**Columnas nuevas**

- `franja_horaria`: la hora en punto de `hora_decimal`. `noche` 22–5, `manana` 6–11, `tarde` 12–17, `tarde-noche` 18–21. `hora_decimal` se conserva también como número.
- `con_moto`: 1 si `motos_implicadas >= 1`. Un recuento ausente cuenta como 0.
- `con_pesado`: 1 si `pesados_implicados >= 1`. Un recuento ausente cuenta como 0.
- `carretera_grupo`: se quedan `M30`, `A2`, `M607`, `A5`, `A4`, `M11` y `A3`. Cualquier otra vía, incluido el vacío, pasa a `Other`.

**Entran tal como quedaron en la limpieza.** `tipo_colision`, `estado_firme`, `tipo_via`, `ubicacion`, `tipo_accidente`, `circulacion`, `distrito` y `vehiculos_implicados`.

**Salen de la tabla.** `heridos_graves` y `victimas_mortales` definen `grave`. `heridos_leves` es un desenlace. `descripcion` queda para la tarea 2.1. También se omiten `numero_incidencia`, `localizacion`, `eje`, `unidad_samur_id`, `fecha`, `hora`, `fecha_calendario`, `tipo_colision_inferido` y `fuera_de_madrid`. `motos_implicadas` y `pesados_implicados` quedan sustituidos por las dos banderas, y `carretera` por `carretera_grupo`.

**Partición.** 80/20 estratificada por `grave` (`random_state` 42). Train: 1569 filas, 36 graves (2,29 %). Test: 393 filas, 9 graves (2,29 %).

## Caso 2.1 — Agente RAG

Consulta los informes de accidentes. No cuenta filas ni calcula medias: busca los informes cuya descripción se parece a la pregunta y responde solo con lo que ha recuperado.

### Datos

El índice parte de `data_clean/accidentes_clean.csv`, la limpieza común descrita arriba. Se indexan las 1860 descripciones no vacías; los 102 partes sin texto (1 grave) quedan fuera.

`2_1_rag/pipeline.py` fue la primera limpieza del caso. Hoy solo se usa su función `infer_tipo_colision`, que rellena los `tipo_colision` vacíos: Claude Sonnet 4.6, a temperatura 0, recibe lotes de 15 partes (`numero_incidencia`, `tipo_accidente` y `descripcion`) y devuelve una de cinco etiquetas (alcance, lateral, frontal, mediana u Otro). El resultado se guarda en `.cache/tipo_colision.json`. Falta validar esas etiquetas con una muestra revisada a mano.

Los metadatos de cada vector son `numero_incidencia`, `distrito` y `fecha`. Falta añadir `grave` y `tipo_colision`: «accidente grave» en el texto no equivale a `grave = 1` (54 partes lo escriben con `grave = 0`), así que esa pregunta debe filtrarse por metadato.

### Arquitectura de embeddings

Cada descripción no vacía es un solo vector. No se trocean: un informe cabe entero en el modelo.

- Modelo local `Qwen/Qwen3-Embedding-0.6B`: 1024 dimensiones y similitud coseno.
- La pregunta lleva la instrucción de búsqueda del modelo. Los documentos se codifican sin esa instrucción.
- Los vectores están en Pinecone serverless (`aws`, `eu-west-1`), en el índice `accidentes-descripcion`.
- `embeddings.py` sube el índice una vez. Si ya hay vectores, no lo repite. `--force` lo rehace.
- `tools.py` expone `buscar_descripciones`, que devuelve los informes más parecidos con su número, distrito y fecha.



### Agente

`agent.py` usa Deep Agents (`create_deep_agent`) con Claude Opus 5.5. El grafo compilado es `__start__ → PatchToolCalls → model ⇄ tools → __end__`; la única herramienta de consulta es `buscar_descripciones` (Deep Agents añade además sus herramientas de ficheros y `task`, que este caso no usa). `MemorySaver` guarda el historial por `thread_id`. La respuesta final es un JSON con una nota y los incidentes (número, distrito, fecha y qué ocurrió). `diagrama_agente.py` dibuja el grafo en `figuras/agente_langgraph.png`.

`api.py` publica ese turno en `POST /chat` con FastAPI, en streaming. El frontend de `2_1_rag/frontend` muestra la cadena de pensamiento, la llamada a la herramienta y la tabla.

### Cómo ejecutarlo

Desde `2_1_rag`, con el entorno activo y las claves en `.env` (`data_clean/accidentes_clean.csv` ya está en el repositorio; para regenerarlo, ejecuta `data_viz/accidentes-analysis.ipynb`):

```
python embeddings.py
python -m uvicorn api:app --port 8000
```

En otra terminal:

```
cd 2_1_rag/frontend
npm install
npm run dev
```

Claves: `ANTHROPIC_API_KEY` y `PINECONE_API_KEY`. Opcionales: `PINECONE_INDEX`, `PINECONE_CLOUD` y `PINECONE_REGION`.

## Caso 2.2 — Agente de clasificación de emergencias

`cleaning/limpieza_tipos_emergencia.py` lee `data/tipos_emergencia.csv` y escribe `data_clean/tipos_emergencia_clean.csv`. No modifica el original. De 33 filas salen 42 tipos.

### Decisiones de limpieza

**Duplicados.** Los ids 100, 101 y 102 repiten los ids 1, 5 y 29 con otra grafía. Se fusionan, como indicó Bluetab, y salen del dataset limpio.

**Se dejan como vienen.** Las 6 columnas originales (`tipo_id`, `codigo`, `categoria`, `requiere_medico`, `tiempo_respuesta_objetivo_min` y `prioridad_base`), aunque traigan grafías mezcladas (`ALTA`, `Si`, `0`) o categorías incoherentes. Las versiones corregidas van en columnas nuevas.

**Columnas nuevas**

- `categoria_correcta`: Médica, Trauma, Psiquiátrica, Intoxicación, Violencia/Social u Otros. Las categorías originales no tenían relación con el tipo (accidente de bicicleta → Intoxicación) y se reasignan todas por criterio clínico. Violencia/Social es nueva.
- `requiere_medico_correcto`: True si el cuadro puede necesitar valoración o intervención médica. False si lo habitual es soporte básico o no hay componente clínico urgente.
- `prioridad_base_correcta`: `alta`, `media` o `baja`, en minúsculas. `alta` es la urgencia máxima.
- `tiempo_respuesta_objetivo_min_correcto`: escala por urgencia. 6 min riesgo vital inmediato, 8 alta, 10–12 media, 15 media-baja, 20 baja y 30 programado.

**Criterio de urgencia y espera.** La urgencia depende del riesgo para la vida y de lo rápido que puede empeorar el paciente sin atención, no de lo frecuente que sea el tipo.

- `alta`: riesgo vital inmediato o potencial (parada cardiorrespiratoria, anafilaxia, inconsciente sin causa, accidentes de alta energía, hemorragia grave). Objetivo de 6 min si el riesgo es inmediato y de 8 si es potencial.
- `media`: hace falta valoración sanitaria, pero el cuadro rara vez es mortal de inmediato (heridas, caídas, estado etílico, violencia de género, agresión sexual). Objetivo de 10–12 min, y 15 si además no hay riesgo vital.
- `baja`: sin riesgo vital, la atención puede esperar o está programada (patología digestiva, psicosomática, certificación psiquiátrica, orden médica). Objetivo de 20 min, y 30 si es un acto programado.
- `requiere_medico_correcto` es True cuando el cuadro puede necesitar intervención médica y False cuando basta el soporte básico (caída, monopatín, bicicleta).

Los valores originales no seguían ninguna lógica: la parada cardiorrespiratoria tenía 11 min y la patología digestiva, prioridad alta con 12 min. Se aplica la misma escala a los 30 tipos originales y a los nuevos para que sean comparables entre sí.

**Tipos nuevos.** Son 12 tipos que aparecen en `activaciones` y no estaban en el catálogo (ids 31–42). Sus columnas originales quedan vacías.

- Urgencia alta: entra siempre, aunque tenga una sola observación.
- Urgencia media o baja: solo si representa al menos el 0,1 % de las activaciones.
- Si dos tipos tienen los mismos valores y el mismo tipo de relato, se unen: más tipos confunden más al agente. Autobús, tren, avión y explosión → "Accidente o suceso grave con múltiples víctimas". Infarto → patología cardiovascular, arrollamiento de tren → atropello, arma de fuego → arma blanca, intoxicación por fármacos → sobredosis.
- Un tipo que absorbe a otros toma la espera más exigente de sus miembros.

**Fuera de catálogo.** Los códigos de recursos enviados (`1 SVB`), las instituciones (`Policía nacional`), los servicios administrativos o de apoyo, los lugares y los registros sin dato no son un tipo de emergencia. El agente los trata como "fuera de catálogo". Con el catálogo limpio, el 96,3 % de las activaciones queda asignado a un tipo (antes, el 92,0 %).

**Límite.** Los valores `_correcto/a` son criterio clínico, no salen de los datos: en `activaciones` la prioridad y el tiempo real hasta la intervención son casi iguales para todos los tipos. Pendiente de validar con Bluetab.

### Agente

El LLM clasifica el `tipo_id` a partir del relato de la emergencia. La categoría, `requiere_medico`, el tiempo objetivo y la prioridad se leen del catálogo limpio. Si el relato no encaja, responde "no está claro" o "fuera de catálogo". En desarrollo.

### Cómo ejecutarlo

Desde `cleaning`, con el entorno activo y la carpeta `data_clean` creada:

```
python limpieza_tipos_emergencia.py
```
