# Preprocesamiento: `distritos.csv`

Documentación técnica del pipeline de limpieza, validación y consolidación de la tabla maestra de distritos de Madrid.

---

## 1. Descripción del Dataset

* **Nombre del archivo:** `distritos.csv`
* **Directorio origen:** `data/raw/`
* **Directorio destino:** `data/clean/distritos_clean.csv`
* **Rol en el proyecto:** **Tabla dimensional maestra (lookup table)**. Contiene los identificadores clave (`id`, `nombre`, `codigo_postal`), métricas base (`poblacion`, `superficie`) y variables dotacionales sanitarias preliminares (`num_hospitales`, `base_samur`).
* **Estructura esperada:** 21 filas (una por distrito oficial de Madrid) y 7 columnas.
* **Política de datos:** Inmutabilidad estricta de `data/raw/`. Toda transformación se efectúa mediante un script automatizado hacia `data/clean/`.

---

## 2. Diagnóstico de Calidad de Datos

| Problema | Ubicación / Registros Afectados | Acción de Mitigación |
| :--- | :--- | :--- |
| **Registros duplicados** | 24 filas en vez de 21.<br>Parejas duplicadas:<br>• Centro (`id` 1 y 22)<br>• Chamartín (`id` 5 y 24)<br>• Tetuán (`id` 6 y 23) | Consolidación (*coalesce*) en un único registro por distrito. Se preserva el identificador canónico más bajo ($1 \le \text{id} \le 21$). |
| **Inconsistencia de nomenclatura** | Variaciones de casing y acentos en filas repetidas (p. ej., `Centro`, `Chamartin`). | Normalización mediante la función estándar `normalizar_distrito` (mayúsculas, sin diacríticos/tildes). |
| **Valores imposibles / Outliers** | `poblacion` en Moratalaz = $-999$. | Reemplazo por valor nulo (`NaN`). |
| **Valores faltantes en Población** | • Centro (fila 1)<br>• San Blas<br>• Barajas | • Centro: recuperado de su registro duplicado.<br>• San Blas y Moratalaz: imputados vía cruce con `socioeconomico_clean.csv`.<br>• Barajas: estimación basada en densidad ($\text{densidad} \times \text{superficie} = 47.703$). |
| **Valores faltantes en Superficie** | Retiro y Salamanca. | Imputación desde `socioeconomico_clean.csv` ($5{,}46\text{ km}^2$ y $5{,}41\text{ km}^2$ respectivamente). |

---

## 3. Pipeline de Limpieza y Transformación

```
data/raw/distritos.csv (24 filas, 7 cols)
   │
   ├── [Paso 0] Lectura exploratoria y perfilado de datos
   ├── [Paso 1] Normalización canónica de distritos (mayúsculas / sin tildes)
   ├── [Paso 2] Resolución y merge de duplicados (IDs 22, 23, 24 consolidados en 1, 6, 5)
   ├── [Paso 3] Saneamiento de valores fuera de rango (-999 a NaN; validación lógica)
   ├── [Paso 4] Cruce e imputación cruzada desde socioeconomico_clean.csv
   ├── [Paso 5] Validación cruzada de consistencia matemática (Población, Superficie, Densidad)
   │
   └── [Paso 6] Exportación final ──> data/clean/distritos_clean.csv (21 filas, 7 cols)
```

### Detalle de las Etapas:

1. **Paso 0 – Inspección y Carga:** Identificación de dimensiones iniciales ($24 \times 7$), detección de registros duplicados por nombre y valor centinela ($-999$).
2. **Paso 1 – Normalización de Entidades:** Aplicación de la función compartida `normalizar_distrito()`, asegurando coincidencia 1:1 con las claves del resto de datasets.
3. **Paso 2 – Deduplicación:** Comprobación de consistencia entre pares duplicados. No se detectaron contradicciones numéricas directas, sino complementariedad (una fila aportaba campos vacíos de la otra). Se combinaron tomando el primer valor no nulo y manteniendo el `id` base ($1$ a $21$).
4. **Paso 3 – Validación de Rango:**
   * Sustitución de $-999 \rightarrow \text{NaN}$.
   * Comprobación de integridad:
     $$\text{superficie} > 0 \quad\land\quad \text{num\_hospitales} \ge 0 \quad\land\quad \text{base\_samur} \in \{0, 1\}$$
5. **Paso 4 – Enriquecimiento e Imputación Cruzada:** Lectura de `data/clean/socioeconomico_clean.csv` para completar valores faltantes de población y superficie.
6. **Paso 5 – Auditoría de Consistencia:**
   * Verificación de paridad entre la población de `distritos_clean.csv` y `socioeconomico_clean.csv`.
   * Validación de densidad:
     $$\frac{\text{poblacion}}{\text{superficie}} \approx \text{densidad}$$
7. **Paso 6 – Serialización:** Guardado del archivo ordenado canónicamente por `id`.

---

## 4. Estado Final del Dataset

* **Dimensiones finales:** 21 filas $\times$ 7 columnas.
* **Completitud:** **100% (0 valores nulos)** en todas las variables.
* **Nota sobre Barajas:** La población asignada ($47.703$) es un valor **estimado matemáticamente** ($\text{densidad} \times \text{superficie}$), al no estar disponible en las fuentes en bruto. Representa el único dato modelado/sintético de la tabla.

---

## 5. Dependencias y Puntos de Decisión

> ⚠️ **Orden de ejecución crítico:**  
> Este script tiene una dependencia directa hacia atrás: **requiere que `socioeconomico_clean.csv` haya sido generado previamente**, ya que de él obtiene superficies faltantes y la estimación poblacional de Barajas.

### Puntos Abiertos para Validación del Equipo:
1. **Validación Externa de Infraestructura Sanitaria:** Las variables `num_hospitales` y `base_samur` deben contrastarse y validarse una vez finalizada la limpieza de las fuentes independientes `hospitales.csv` y `bases_samur.csv`.
2. **Confirmación de Población de Barajas:** Validar con el cliente/empresa si se acepta el valor sintético de $47.703$ habitantes o si existe una cifra oficial censal para reemplazarlo.