# Caso 2.2 — Propuesta tecnológica

Resumen de la presentación para Bluetab: una slide por decisión.

| Decisión | Elegido | Abierto |
|---|---|---|
| Partir el texto | Una ficha por tipo, con síntomas y sinónimos | — |
| Dónde vive el catálogo | Entero en el prompt; las reglas se leen del CSV | — |
| Arquitectura | Comparar varias: una llamada, recuperar y clasificar, grafo por pasos | Si se añade un clasificador sin LLM |
| Relato ambiguo | Preguntar al operador | Cuántas preguntas como máximo |
| Datos sintéticos | Para evaluar y como ejemplos en el prompt (conjuntos separados) | Cuántos relatos por tipo |
| Métricas | Infra-triaje (la crítica), macro-F1, preguntas, coste y latencia | — |

**Idea general:** el LLM elige el `tipo_id` del relato. Si duda, pregunta al operador. La prioridad, el médico y el tiempo objetivo salen del catálogo limpio.
