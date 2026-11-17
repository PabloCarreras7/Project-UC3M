# Cierre del caso 1.3: segmentación y análisis socioeconómico

Material de cierre de la parte 1.3. El baseline `clustering_distritos.ipynb` se conserva como histórico; el modelo principal está en `segmentacion_final_distritos.ipynb`.

## Contenido y ejecución

El notebook final contiene carga y comprobaciones de integridad, selección de variables, escalado min-max, comparación KMeans/Ward/DBSCAN, elección de k, perfiles y mapas, robustez, análisis socioeconómico directo y conclusiones. Se ejecuta de arriba abajo. Las comprobaciones `assert` detienen la ejecución si las entradas no cumplen lo esperado.

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
