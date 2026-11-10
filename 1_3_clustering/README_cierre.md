# Cierre del caso 1.3: segmentación y análisis socioeconómico

Material de cierre de la parte 1.3 (clustering + análisis socioeconómico). Continúa el baseline de `clustering_distritos.ipynb`, que queda como histórico.

## Contenido

- `segmentacion_final_distritos.ipynb` — notebook final, ejecutable de arriba abajo. Contiene:
  1. Carga y comprobaciones de integridad de las tablas (se paran con `assert` si algo cambia).
  2. Selección de variables con las cuatro reglas del baseline (auditable en el mapa de calor de correlaciones).
  3. Elección de algoritmo y de *k* por ensayo y error documentado (k-means y Ward con k = 2…8, DBSCAN descartado con motivo).
  4. Modelo final (k-means, k = 3) y perfiles de los tres grupos.
  5. Mapa de Madrid por grupos.
  6. Robustez de la partición (semillas, sin Centro, sin imputados, sin variables sociales, Ward).
  7. Análisis socioeconómico: tiempos de respuesta, demanda por habitante, tipología por grupo, noche, estacionalidad, prioridad y oferta frente a demanda.
  8. Conclusiones con las limitaciones dichas explícitamente.
- `graficos_cierre/` — las 13 figuras que genera el notebook (numeradas 00-12), listas para las diapositivas.
- `distritos_madrid.geojson` — límites oficiales de distrito (Ayuntamiento de Madrid). El notebook lo vuelve a descargar si no está.

## Datos de entrada (nada se vuelve a limpiar)

- `tabla_distritos.csv` y `tabla_distritos_norm.csv` (esta carpeta).
- `data_clean/activaciones_limpio.csv` y `data_clean/tipos_emergencia_clean.csv`.

## Decisiones clave (resumen)

- Las 3 columnas con celdas desconocidas (`unidades_samur`, `num_hospitales_cat`, `camas_hospital`) se excluyen del clustering: no se imputa lo que no se sabe. Detalle en `README_recursos_samur.md`. La oferta se analiza aparte con lo conocido (bases).
- k-means con k = 3, elegido por silueta, codo e interpretabilidad; la robustez se mide con ARI y se reporta tal cual (estable, pero exploratorio: 21 distritos).
- Marco honesto en todo el notebook: correlaciones, no causalidad; sin afirmaciones de significación estadística.
