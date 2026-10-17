# Project-UC3M

Casos de uso con datos de emergencias del SAMUR de Madrid (proyecto con Bluetab).

## Estructura
- data/            datos originales (no modificar)
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
|---|---|
| 1.1 | Bea |
| 1.2 | Lukas|
| 1.3 | Diego |
| 2.1 | Dani |
| 2.2 | Pablo |

## Normas de trabajo
- Cada uno trabaja en su rama (ej. caso-2.2-limpieza).
- Nada entra en main sin pull request.
- Nunca subir claves ni el fichero .env.

## Caso 2.1 — Agente RAG

Consulta los informes de accidentes. No cuenta filas ni calcula medias: busca los informes cuya descripción se parece a la pregunta y responde solo con lo que ha recuperado.

### Por qué se procesan los datos

`data/accidentes.csv` no se puede consultar tal cual.

- Hay 100 números de incidencia repetidos. Cada pareja es el mismo accidente, con la misma hora y la misma localización. El proceso se queda con una fila y completa los huecos (descripción, tipo de colisión, etc.) con la otra.
- `fecha` mezcla día/mes, mes/día e ISO. 44 valores no coinciden con la fecha que ya va en el número de incidencia. La fecha de salida es esa, en formato `YYYY-MM-DD`. La hora queda en `HH:MM:SS`.
- `tipo_via`, `estado_firme` y `circulacion` repiten el mismo valor con distinta escritura. `0`, `_` y `(En blanco)` se dejan vacíos. `M607` pasa a `M-607`.
- 80 filas no tienen `tipo_colision`. Si hay descripción, Claude la lee y elige una clase de las que ya usa el dataset: alcance, lateral, frontal, mediana u otro. Sin descripción el campo sigue vacío.

`2_1_rag/pipeline.py` lee el CSV original y escribe `data/accidentes_clean.csv`. No modifica `accidentes.csv`. De 2062 filas salen 1962. Añade `hora_decimal` y `grave` (1 si hay heridos graves o víctimas mortales).

### Arquitectura de embeddings

Cada descripción no vacía es un solo vector. No se trocean: un informe cabe entero en el modelo.

- Modelo local `Qwen/Qwen3-Embedding-0.6B`: 1024 dimensiones y similitud coseno.
- La pregunta lleva la instrucción de búsqueda del modelo. Los documentos se codifican sin esa instrucción.
- Los vectores están en Pinecone serverless (`aws`, `eu-west-1`), en el índice `accidentes-descripcion`.
- `embeddings.py` sube el índice una vez. Si ya hay vectores, no lo repite. `--force` lo rehace.
- `tools.py` expone `buscar_descripciones`, que devuelve los informes más parecidos con su número, distrito y fecha.

### Agente

`agent.py` usa Deep Agents con Claude Opus. La única herramienta de consulta es `buscar_descripciones`. No hay subagentes. La respuesta final es un JSON con una nota y los incidentes (número, distrito, fecha y qué ocurrió).

`api.py` publica ese turno en `POST /chat` con FastAPI, en streaming. El frontend de `2_1_rag/frontend` muestra la cadena de pensamiento, la llamada a la herramienta y la tabla.

### Cómo ejecutarlo

Desde `2_1_rag`, con el entorno activo y las claves en `.env`:

```
python pipeline.py
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
