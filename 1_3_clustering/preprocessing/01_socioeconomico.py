# =============================================================================
# socioeconomico.csv
# # Cada bloque "# %%" es una celda (VS Code / Spyder / Jupyter). Ejecutar en orden.
# Uso desde terminal:  python 01_socioeconomico.py
# =============================================================================
# %% PASO 0 - Cargar y mirar los datos
import unicodedata
from pathlib import Path
import numpy as np
import pandas as pd

RAW = Path("raw")      # carpeta con los CSV originales (nunca se editan)
OUT = Path("clean")    # carpeta donde se guarda lo limpio
OUT.mkdir(exist_ok=True)

soc = pd.read_csv(RAW / "socioeconomico.csv")
print(soc.shape)              # (24, 14): 24 filas, deberian ser 21 distritos
print(soc.dtypes)             # num_centros_salud sale 'object' -> hay texto
print(soc.isna().sum())       # huecos originales

# %% PASO 1 - Normalizar los nombres de distrito
OFICIALES = ["CENTRO", "ARGANZUELA", "RETIRO", "SALAMANCA", "CHAMARTIN", "TETUAN", "CHAMBERI",
             "FUENCARRAL-EL PARDO", "MONCLOA-ARAVACA", "LATINA", "CARABANCHEL", "USERA",
             "PUENTE DE VALLECAS", "MORATALAZ", "CIUDAD LINEAL", "HORTALEZA", "VILLAVERDE",
             "VILLA DE VALLECAS", "VICALVARO", "SAN BLAS-CANILLEJAS", "BARAJAS"]
ALIAS = {"FUENCARRAL": "FUENCARRAL-EL PARDO", "MONCLOA": "MONCLOA-ARAVACA",
         "SAN BLAS": "SAN BLAS-CANILLEJAS"}

def normalizar_distrito(nombre):
    """Mayusculas, sin tildes ni espacios sobrantes; despues aplica los alias."""
    if pd.isna(nombre):
        return None
    s = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode()
    s = " ".join(s.upper().split())
    s = ALIAS.get(s, s)
    return s if s in OFICIALES else None   # None = nombre no reconocido

soc["distrito"] = soc["distrito"].map(normalizar_distrito)
assert soc["distrito"].notna().all(), "Hay distritos que no se reconocen"

# %% PASO 2 - Columnas numericas: convertir texto a numero
PALABRAS = {"cero": 0, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
            "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12}

def a_numero(x):
    if pd.isna(x):
        return np.nan
    s = str(x).strip().lower()
    return float(PALABRAS[s]) if s in PALABRAS else pd.to_numeric(s, errors="coerce")  # 'N/A' -> NaN

cols_num = [c for c in soc.columns if c != "distrito"]
for c in cols_num:
    soc[c] = soc[c].map(a_numero)

# %% PASO 3 - Duplicados: un distrito, una fila
dup = soc[soc.duplicated("distrito", keep=False)].sort_values("distrito")
print(dup[["distrito", "indice_vulnerabilidad", "num_centros_salud", "densidad_hab_km2"]])

# ¿Hay duplicados que se contradigan? (dos valores distintos no nulos)
conflictos = soc.groupby("distrito")[cols_num].nunique() > 1
print("Conflictos:", conflictos.stack()[lambda s: s].index.tolist())  # solo Centro/densidad (28626.8 vs 28627.0)

# first() coge el primer valor NO nulo de cada columna -> completa los huecos de un duplicado con el otro
soc = soc.groupby("distrito", as_index=False).first()
assert len(soc) == 21

# %% PASO 4 - Valores imposibles -> NaN
RANGOS = {"poblacion_2024": (1, None), "superficie_km2": (0.1, None), "renta_media_hogar": (1, None),
          "edad_media": (15, 90), "pct_mayores_65": (0, 100), "pct_extranjeros": (0, 100),
          "tasa_paro": (0, 100), "indice_vulnerabilidad": (0, 1), "num_centros_salud": (0, None),
          "num_colegios": (0, None), "num_comisarias": (0, None),
          "parques_m2_habitante": (0, None), "densidad_hab_km2": (1, None)}
for col, (minimo, maximo) in RANGOS.items():
    malo = pd.Series(False, index=soc.index)
    if minimo is not None: malo |= soc[col] < minimo
    if maximo is not None: malo |= soc[col] > maximo
    if malo.any():
        print(col, soc.loc[malo, ["distrito", col]].values.tolist())
    soc.loc[malo, col] = np.nan

# %% PASO 5 - Rellenar poblacion cruzando con distritos.csv
dis = pd.read_csv(RAW / "distritos.csv")
dis["nombre"] = dis["nombre"].map(normalizar_distrito)
dis.loc[dis["poblacion"] <= 0, "poblacion"] = np.nan          # -999 de Moratalaz
dis = dis.groupby("nombre").first()                            # fusiona Centro/Tetuan/Chamartin repetidos

soc = soc.set_index("distrito")
soc["poblacion_2024"] = soc["poblacion_2024"].fillna(dis["poblacion"])
soc["superficie_km2"] = soc["superficie_km2"].fillna(dis["superficie_km2"])
# Si sigue faltando (Barajas): poblacion = densidad x superficie
falta = soc["poblacion_2024"].isna()
soc.loc[falta, "poblacion_2024"] = (soc.loc[falta, "densidad_hab_km2"] * soc.loc[falta, "superficie_km2"]).round()
print("Poblacion estimada para:", soc.index[falta].tolist())

# %% PASO 6 - Comprobar que los datos son coherentes
ratio = (soc["poblacion_2024"] / soc["superficie_km2"]) / soc["densidad_hab_km2"]
assert ratio.between(0.98, 1.02).all(), ratio[~ratio.between(0.98, 1.02)]   # densidad = pob/superficie

# %% PASO 7 - Guardar la version limpia (los NaN se quedan)
soc = soc.reindex(OFICIALES).reset_index()                     # orden oficial, 21 filas
soc.insert(0, "distrito_id", range(1, 22))
soc.to_csv(OUT / "socioeconomico_clean.csv", index=False)
print(soc.shape)                                               # (21, 15)
print(soc.isna().sum()[soc.isna().sum() > 0])                  # huecos que quedan (sin imputar)
