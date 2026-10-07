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
| 1.1 | (completar) |
| 1.2 | (completar) |
| 1.3 | (completar) |
| 2.1 | (completar) |
| 2.2 | Pablo |

## Normas de trabajo
- Cada uno trabaja en su rama (ej. caso-2.2-limpieza).
- Nada entra en main sin pull request.
- Nunca subir claves ni el fichero .env.
