# Limpieza de data/tipos_emergencia.csv -> data_clean/tipos_emergencia_clean.csv
# Caso 2.2. Solo transforma el dataset original en el limpio; la documentación va en el anexo.

# %% 1. Cargar el original (todo como texto, para no alterar nada)
import pandas as pd

df = pd.read_csv("../data/tipos_emergencia.csv", dtype=str)
df["tipo_id"] = df["tipo_id"].astype(int)
print(df.shape)   # (33, 6)

# %% 2. Quitar los duplicados que Bluetab pidió fusionar
# 100 "INTOXICACION ETILICA" -> 1 | 101 "Herida" -> 5 | 102 "CAIDA" -> 29
DUPLICADOS = [100, 101, 102]
df = df[~df["tipo_id"].isin(DUPLICADOS)].copy()
print(df.shape)   # (30, 6)

# %% 3. Valores correctos de los 30 tipos originales
# Orden: (tipo_id, categoria, requiere_medico, espera_min, urgencia)
# Criterio: ver anexo (apartados 4 a 7 y 14). Los tipos que absorben a otros
# ya llevan la espera más exigente de sus miembros (4, 24, 25 y 26).
CORRECTOS_ORIGINALES = [
    (1, 'Intoxicación', True, 12, 'media'),
    (2, 'Trauma', True, 10, 'media'),
    (3, 'Otros', False, 12, 'media'),
    (4, 'Médica', True, 6, 'alta'),
    (5, 'Trauma', True, 12, 'media'),
    (6, 'Médica', True, 6, 'alta'),
    (7, 'Médica', True, 8, 'alta'),
    (8, 'Médica', True, 8, 'alta'),
    (9, 'Otros', False, 10, 'media'),
    (10, 'Psiquiátrica', True, 30, 'baja'),
    (11, 'Trauma', False, 15, 'media'),
    (12, 'Trauma', True, 8, 'alta'),
    (13, 'Otros', False, 20, 'baja'),
    (14, 'Médica', True, 30, 'baja'),
    (15, 'Psiquiátrica', False, 20, 'baja'),
    (16, 'Violencia/Social', False, 12, 'media'),
    (17, 'Trauma', True, 8, 'alta'),
    (18, 'Intoxicación', False, 20, 'baja'),
    (19, 'Intoxicación', True, 8, 'alta'),
    (20, 'Médica', True, 10, 'media'),
    (21, 'Trauma', False, 12, 'media'),
    (22, 'Trauma', False, 12, 'media'),
    (23, 'Médica', True, 6, 'alta'),
    (24, 'Trauma', True, 6, 'alta'),
    (25, 'Violencia/Social', True, 12, 'media'),
    (26, 'Trauma', True, 6, 'alta'),
    (27, 'Médica', False, 20, 'baja'),
    (28, 'Médica', True, 8, 'alta'),
    (29, 'Trauma', False, 15, 'media'),
    (30, 'Médica', True, 6, 'alta'),
]

COLS_NUEVAS = [
    "categoria_correcta",
    "requiere_medico_correcto",
    "tiempo_respuesta_objetivo_min_correcto",
    "prioridad_base_correcta",
]
correctos = pd.DataFrame(CORRECTOS_ORIGINALES, columns=["tipo_id"] + COLS_NUEVAS)

# %% 4. Unir lo correcto a los originales (las 6 columnas originales no se tocan)
# validate="1:1" falla si algún tipo_id estuviera repetido o faltara
df = df.merge(correctos, on="tipo_id", how="left", validate="1:1")

# %% 5. Tipos nuevos (12). Sus columnas originales quedan vacías.
# Orden: (tipo_id, codigo, categoria, requiere_medico, espera_min, urgencia)
NUEVOS = [
    (31, 'Patología neurológica', 'Médica', True, 8, 'alta'),
    (32, 'Maltrato a menores y ancianos', 'Violencia/Social', True, 12, 'media'),
    (33, 'Precipitado', 'Trauma', True, 6, 'alta'),
    (34, 'Patología médica no urgente (infecciosa, urológica, ginecológica)', 'Médica', False, 20, 'baja'),
    (35, 'Autolisis (traumática y no traumática)', 'Psiquiátrica', True, 6, 'alta'),
    (36, 'Accidente o suceso grave con múltiples víctimas', 'Trauma', True, 6, 'alta'),
    (37, 'Atrapamientos y derrumbamientos', 'Trauma', True, 8, 'alta'),
    (38, 'Riesgo químico', 'Intoxicación', True, 8, 'alta'),
    (39, 'Ahogado', 'Médica', True, 6, 'alta'),
    (40, 'Quemado', 'Trauma', True, 8, 'alta'),
    (41, 'Electrocutado', 'Trauma', True, 6, 'alta'),
    (42, 'Riesgo biológico', 'Médica', True, 8, 'alta'),
]
nuevos = pd.DataFrame(NUEVOS, columns=["tipo_id", "codigo"] + COLS_NUEVAS)

clean = pd.concat([df, nuevos], ignore_index=True)

# %% 6. Comprobaciones antes de guardar
assert len(clean) == 42
assert clean["tipo_id"].is_unique
assert clean[COLS_NUEVAS].notna().all().all()
assert set(clean["prioridad_base_correcta"]) <= {"alta", "media", "baja"}
assert set(clean["categoria_correcta"]) <= {"Médica", "Trauma", "Psiquiátrica", "Intoxicación", "Violencia/Social", "Otros"}
assert clean["requiere_medico_correcto"].isin([True, False]).all()
print(clean.shape)  # (42, 10)

# %% 7. Guardar (la carpeta data_clean/ debe existir)
clean.to_csv("../data_clean/tipos_emergencia_clean.csv", index=False)
