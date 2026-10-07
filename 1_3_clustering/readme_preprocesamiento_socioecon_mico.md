# Preprocesamiento: `socioeconomico.csv`

Documentación detallada del pipeline de limpieza, control de calidad y transformación del dataset socioeconómico distrital de Madrid (Caso 1.3).

---

## 1. Descripción del Dataset

* **Nombre del archivo:** `socioeconomico.csv`
* **Directorio origen:** `data/raw/`
* **Directorio destino:** `data/clean/socioeconomico_clean.csv`
* **Alcance:** Contiene indicadores demográficos, económicos y dotacionales de los distritos de Madrid: población, superficie, renta media, edad media, porcentaje de mayores de 65 años, porcentaje de población extranjera, tasa de paro, índice de vulnerabilidad, infraestructuras (centros de salud, colegios, comisarías, parques) y densidad.
* **Estructura esperada:** 21 filas (una por distrito municipal oficial) y 14 variables base.
* **Política de datos:** Inmutabilidad del dato original. El dataset en `raw/` no se modifica; todo el procesamiento se ejecuta vía script determinista y reproducible hacia `clean/`.

---

## 2. Diagnóstico de Calidad de Datos (Problemas Detectados)

| Categoría | Detalle del Problema | Distritos Afectados | Acción Tomada |
| :--- | :--- | :--- | :--- |
| **Duplicados** | 24 filas en lugar de 21 | Centro, Tetuán, Salamanca | Fusión (*merge*) priorizando registros completos. |
| **Inconsistencia de Nombres** | Mezcla de mayúsculas, minúsculas, tildes y variantes | `centro`, `Centro`, `Salamanca`, `FUENCARRAL`, `MONCLOA`, `San Blas` | Normalización canónica a formato oficial (mayúsculas, sin tildes). |
| **Tipado Erróneo** | Cadenas de texto en campo cuantitativo (`num_centros_salud`) | Chamberí (`"ocho"`), San Blas (`"N/A"`) | Parsing de `"ocho"` $\rightarrow$ `8`; `"N/A"` $\rightarrow$ `NaN`. Conversión a numérico. |
| **Valores Fuera de Rango / Imposibles** | 6 registros con anomalías severas | - Barajas: `poblacion = -999`<br>- Chamartín: `pct_mayores_65 = -4.9`<br>- C. Lineal: `pct_mayores_65 = -4.98`<br>- Moncloa: `tasa_paro = 118.1`<br>- Hortaleza: `tasa_paro = 116.3`<br>- Carabanchel: `indice_vulnerabilidad = 1.5` | Reemplazo por `NaN`. No se corrige heurísticamente para evitar sesgos sin validación externa. |
| **Missing Values Originales** | Celdas vacías en origen | Retiro y C. Lineal (renta); V. de Vallecas (paro); Barajas (vulnerabilidad) | Preservados como `NaN` para la fase de imputación. |
| **Registro Faltante Crítico** | Población ausente en `socioeconomico.csv` y `distritos.csv` | Barajas | Reconstrucción analítica: $\text{Población} = \text{Densidad} \times \text{Superficie} = 47.703$ hab. Se etiqueta como dato estimado. |

---

## 3. Pipeline de Limpieza (`steps`)

```text
[raw/socioeconomico.csv]
       │
       ▼
 [Paso 0] Carga e inspección exploratoria de esquema y tipados
       │
       ▼
 [Paso 1] Normalización de nombres de distritos (`normalizar_distrito()`)
       │
       ▼
 [Paso 2] Casteo de columnas numéricas (coerción de cadenas a float/int)
       │
       ▼
 [Paso 3] Deduplicación y consolidación de registros (resolución de conflictos)
       │
       ▼
 [Paso 4] Filtrado por dominios válidos (conversión de valores anómalos a NaN)
       │
       ▼
 [Paso 5] Enriquecimiento y reconstrucción cruzada con `distritos.csv`
       │
       ▼
 [Paso 6] Validación de consistencia cruzada (Densidad vs. Población/Superficie)
       │
       ▼
 [Paso 7] Exportación ordenada a [clean/socioeconomico_clean.csv]
```

### Detalle de Implementación

1. **Paso 0 - Carga y profiling:** Detección de la dimensión incorrecta ($24 \times 14$) y campos categóricos no deseados en `num_centros_salud`.
2. **Paso 1 - Función reutilizable:** Implementación de `normalizar_distrito(nombre)`. Disponible como módulo para el resto del equipo para asegurar consistencia en futuros *joins*.
3. **Paso 2 - Coerción numérica:** Conversión estricta a tipos numéricos, mapeando strings textuales conocidos.
4. **Paso 3 - Resolución de duplicados:** Comprobación de consistencia entre registros duplicados. Solo la densidad de Centro presentaba discrepancia marginal ($28.626,8$ vs $28.627,0$). Se aplicó un *coalesce* (primer valor no nulo), lo que permitió a Tetuán recuperar `indice_vulnerabilidad = 0.55` y `num_centros_salud = 6`.
5. **Paso 4 - Reglas de dominio:**
   * Porcentajes: $[0, 100]$
   * Índice de vulnerabilidad: $[0, 1]$
   * Indicadores demográficos absolutos: $\ge 0$
6. **Paso 5 - Cruzado relacional:** Relleno de métricas espaciales/poblacionales faltantes con `distritos.csv`. Estimación determinista para Barajas.
7. **Paso 6 - Validación matemática:** Comprobación de la fórmula:
   $$\left| \text{densidad} - \frac{\text{población}}{\text{superficie}} \right| \le 0.02 \times \text{densidad}$$
   El 100% de los distritos cumplió el criterio de tolerancia ($\le 2\%$).
8. **Paso 7 - Generación del artefacto:** Incorporación de la clave primaria canónica `distrito_id` y ordenación estándar.

---

## 4. Estado Final del Dataset (`clean`)

* **Dimensiones:** 21 filas $\times$ 15 columnas (incluye clave `distrito_id`).
* **Calidad estructural:** Sin duplicados, tipos validados, nombres normalizados.
* **Mapa de valores ausentes (10 nulos en 5 variables):**
  * `renta_media_hogar` (2): Retiro, Ciudad Lineal
  * `pct_mayores_65` (2): Chamartín, Ciudad Lineal
  * `tasa_paro` (3): Moncloa, Hortaleza, Villa de Vallecas
  * `indice_vulnerabilidad` (2): Carabanchel, Barajas
  * `num_centros_salud` (1): San Blas

---

## 5. Puntos de Validación con el Equipo / Negocio

1. **Dominio del Índice de Vulnerabilidad:** Se asumió el intervalo $[0, 1]$, lo que provocó el descarte del valor $1.5$ de Carabanchel. Pendiente confirmar con Bluetab si la métrica admite valores fuera de escala normalizada (por ejemplo, índices base 100 o percentiles).
2. **Tratamiento del error de escala en Paro:** Los valores $118.1$ (Moncloa) y $116.3$ (Hortaleza) parecen un desplazamiento tipográfico de coma decimal ($11.8\%$ y $11.6\%$). Ante la falta de confirmación oficial, se han dejado como `NaN` para evitar introducir datos no verificados.
3. **Impacto de la dimensionalidad:** Hay 10 valores ausentes sobre una muestra pequeña ($N = 21$). Cualquier técnica de imputación tendrá un peso sustancial en análisis posteriores (distancias, clusters, PCA).

---

## 6. Próximos Pasos (Backlog)

- [ ] **Estrategia de Imputación:** Implementar imputación multivariante basada en vecinos más cercanos (KNN con $k=3$) utilizando variables correlacionadas no nulas.
- [ ] **Análisis de Sensibilidad:** Ejecutar los modelos de clustering (Caso 1.3) bajo dos escenarios:
  1. Dataset con registros disponibles / imputación simple.
  2. Dataset post-imputación KNN.
  Evaluar la variación del Silhouette Score y la estabilidad de asignación de clústeres.