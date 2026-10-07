# =============================================================================
# distritos.csv
# Cada bloque "# %%" es una celda (VS Code / Spyder / Jupyter). Ejecutar en orden.
# Requiere haber ejecutado antes 01_socioeconomico.py (usa clean/socioeconomico_clean.csv)
# Uso desde terminal (en la raiz del repo):  python 1_3_clustering/preprocessing/02_distritos.py
# =============================================================================
# %% PASO 0 - Cargar y mirar los datos
import unicodedata
from pathlib import Path
import numpy as np
import pandas as pd

# --- Rutas (funcionan desde cualquier sitio dentro del repo) ---------------------
# Estructura esperada:  <repo>/data/...   y   <repo>/1_3_clustering/preprocessing/este_script.py
try:
    AQUI = Path(__file__).resolve().parent
except NameError:                      # si se ejecuta como celdas/notebook: abrir desde esta carpeta
    AQUI = Path.cwd()
CASO = AQUI.parent                     # 1_3_clustering/
DATA = CASO.parent / "data"            # datos originales (no se modifican)
OUT = CASO / "data_clean"              # aqui se guarda lo limpio
OUT.mkdir(exist_ok=True)

def buscar(nombre):
    """Localiza un CSV original dentro de data/ (aunque este en una subcarpeta)."""
    return next(DATA.rglob(nombre))

dis = pd.read_csv(buscar("distritos.csv"))
print(dis.shape)               # (24, 7): deberian ser 21 distritos
print(dis.isna().sum())        # poblacion y superficie con huecos
print(dis["poblacion"].min())  # -999 -> valor centinela

# %% PASO 1 - Normalizar los nombres (misma funcion que en socioeconomico)
OFICIALES = ["CENTRO", "ARGANZUELA", "RETIRO", "SALAMANCA", "CHAMARTIN", "TETUAN", "CHAMBERI",
             "FUENCARRAL-EL PARDO", "MONCLOA-ARAVACA", "LATINA", "CARABANCHEL", "USERA",
             "PUENTE DE VALLECAS", "MORATALAZ", "CIUDAD LINEAL", "HORTALEZA", "VILLAVERDE",
             "VILLA DE VALLECAS", "VICALVARO", "SAN BLAS-CANILLEJAS", "BARAJAS"]
ALIAS = {"FUENCARRAL": "FUENCARRAL-EL PARDO", "MONCLOA": "MONCLOA-ARAVACA",
         "SAN BLAS": "SAN BLAS-CANILLEJAS"}

def normalizar_distrito(nombre):
    if pd.isna(nombre):
        return None
    s = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode()
    s = " ".join(s.upper().split())
    s = ALIAS.get(s, s)
    return s if s in OFICIALES else None

dis["nombre"] = dis["nombre"].map(normalizar_distrito)
assert dis["nombre"].notna().all(), "Hay distritos que no se reconocen"

# %% PASO 2 - Duplicados: un distrito, una fila
dup = dis[dis.duplicated("nombre", keep=False)].sort_values("nombre")
print(dup)   # Centro (ids 1 y 22), Chamartin (5 y 24), Tetuan (6 y 23)

# Conflictos: valores distintos no nulos (el distrito_id siempre difiere, no cuenta)
cols = [c for c in dis.columns if c not in ("nombre", "distrito_id")]
conflictos = dis.groupby("nombre")[cols].nunique() > 1
print("Conflictos:", conflictos.stack()[lambda s: s].index.tolist())   # ninguno

# first() = primer valor NO nulo de cada columna. Se conserva el id mas bajo (1..21)
dis = dis.groupby("nombre", as_index=False).first()
assert len(dis) == 21

# %% PASO 3 - Valores imposibles -> NaN
malo = dis["poblacion"] <= 0
print(dis.loc[malo, ["nombre", "poblacion"]])      # Moratalaz = -999
dis.loc[malo, "poblacion"] = np.nan
assert (dis["superficie_km2"].dropna() > 0).all()
assert (dis["num_hospitales"] >= 0).all()
assert dis["base_samur"].isin([0, 1]).all()

# %% PASO 4 - Rellenar poblacion y superficie con socioeconomico_clean
soc = pd.read_csv(OUT / "socioeconomico_clean.csv").set_index("distrito")
dis = dis.set_index("nombre")
for col, col_soc in [("poblacion", "poblacion_2024"), ("superficie_km2", "superficie_km2")]:
    falta = dis[col].isna()
    print(col, "rellenado desde socioeconomico:", dis.index[falta].tolist())
    dis.loc[falta, col] = soc.loc[dis.index[falta], col_soc]
# OJO: la poblacion de Barajas no existe en ningun fichero; en 01 se estimo como densidad x superficie

# %% PASO 5 - Comprobar coherencia
assert dis[["poblacion", "superficie_km2"]].notna().all().all()
dif = (dis["poblacion"] - soc["poblacion_2024"]).abs()
assert (dif < 1).all()                                         # misma poblacion en los dos ficheros
densidad = dis["poblacion"] / dis["superficie_km2"]
assert (densidad / soc["densidad_hab_km2"]).between(0.98, 1.02).all()

# %% PASO 6 - Guardar
dis = dis.reindex(OFICIALES).reset_index()
dis["distrito_id"] = range(1, 22)
dis = dis[["distrito_id", "nombre", "codigo_postal_principal", "poblacion",
           "superficie_km2", "num_hospitales", "base_samur"]]
for c in ["distrito_id", "codigo_postal_principal", "poblacion", "num_hospitales", "base_samur"]:
    dis[c] = dis[c].astype(int)
dis.to_csv(OUT / "distritos_clean.csv", index=False)
print(dis.shape)               # (21, 7)
print(dis.isna().sum().sum())  # 0 nulos
