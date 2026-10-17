"""Limpia data/accidentes.csv y escribe data/accidentes_clean.csv.

    python pipeline.py

Qué hace, a partir del análisis del CSV original (2062 filas):

- Quita el duplicado mutuo. Hay 100 números de incidencia repetidos, siempre
  por parejas, con la misma hora y la misma localización. Se conserva una fila
  y se rellenan los huecos con la otra (descripción, tipo de colisión, etc.).
- La fecha del CSV mezcla DD/MM/YYYY, MM/DD/YYYY e ISO, y a veces no coincide
  con el número de incidencia. La fecha de salida es la del número
  (AAAAMMDD), en formato YYYY-MM-DD. La hora queda en HH:MM:SS y se añade
  hora_decimal.
- Unifica tipo de vía, estado del firme y circulación. Los valores 0, _ y
  "(En blanco)" pasan a nulo. M607 pasa a M-607.
- grave vale 1 si hay heridos graves o víctimas mortales.
- Los tipo_colision vacíos se infieren con Claude leyendo la descripción.
  Sin descripción se dejan vacíos. El resultado se cachea en .cache/.
"""

import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "accidentes.csv"
TARGET = ROOT / "data" / "accidentes_clean.csv"
CACHE = ROOT / ".cache" / "tipo_colision.json"

LABELS = {
    "colision por alcance": "COLISIÓN POR ALCANCE",
    "colision lateral": "COLISIÓN LATERAL",
    "colision frontal": "COLISIÓN FRONTAL",
    "colision mediana": "COLISIÓN MEDIANA",
    "otro": "Otro",
}

TIPO_VIA = {
    "tronco": "TRONCO",
    "via de servicio": "VIA DE SERVICIO",
    "ramal": "RAMAL",
    "transfer": "TRANSFER",
    "tablero": "TABLERO",
    "tunel": "TUNEL",
}

ESTADO_FIRME = {
    "seco": "Seco y limpio",
    "seco y limpio": "Seco y limpio",
    "mojado": "Mojado",
    "humedo": "Húmedo",
    "húmedo": "Húmedo",
    "otros": "Otros",
}

FILL_FROM_DUPLICATE = (
    "descripcion",
    "tipo_colision",
    "estado_firme",
    "circulacion",
    "unidad_samur_id",
    "carretera",
)

CLASSIFIER_PROMPT = """Eres un clasificador de accidentes de tráfico de Madrid.
Lee cada descripción y elige un solo tipo_colision.
Responde únicamente con un JSON: una lista de objetos con numero_incidencia y tipo_colision.

Valores permitidos, escritos exactamente así:
- COLISIÓN POR ALCANCE: un vehículo golpea a otro por detrás. Incluye "alcance" y "alcance lateral" si el golpe principal es por detrás.
- COLISIÓN LATERAL: golpe de costado entre vehículos, cambio de carril o roce lateral, sin ser un alcance.
- COLISIÓN FRONTAL: choque de frente entre dos vehículos.
- COLISIÓN MEDIANA: el vehículo impacta contra la mediana, el new jersey central o la barrera del margen, y no hay un choque entre vehículos que encaje arriba.
- Otro: aviso anulado, atropello, vuelco sin impacto claro, caída de carga, solo restos, muro o hastial sin mediana, o la descripción no dice cómo fue el golpe.

La descripción manda sobre tipo_accidente. Si dice alcance, es COLISIÓN POR ALCANCE."""


def _filled(value: object) -> bool:
    if value is None:
        return False
    try:
        if pd.isna(value):
            return False
    except TypeError:
        pass
    return not (isinstance(value, str) and not value.strip())


def _fold(text: str) -> str:
    table = str.maketrans("áéíóúü", "aeiouu")
    return text.strip().casefold().translate(table)


def load_raw() -> pd.DataFrame:
    data = pd.read_csv(SOURCE)
    text_columns = [column for column in data.columns if pd.api.types.is_string_dtype(data[column])]
    for column in text_columns:
        data[column] = data[column].map(lambda value: value.strip() if isinstance(value, str) else value)
        data.loc[data[column].eq(""), column] = pd.NA
    return data


def keep_mutual_accident(group: pd.DataFrame) -> pd.Series:
    """Una fila por numero_incidencia. La pareja es el mismo accidente."""
    ranked = group.copy()
    ranked["_score"] = sum(ranked[column].map(_filled).astype(int) for column in FILL_FROM_DUPLICATE)
    ranked["_length"] = ranked["descripcion"].fillna("").astype(str).str.len()
    ranked = ranked.sort_values(["_score", "_length"], ascending=False)
    kept = ranked.iloc[0].copy()
    for column in FILL_FROM_DUPLICATE:
        if _filled(kept[column]):
            continue
        for value in ranked[column].iloc[1:]:
            if _filled(value):
                kept[column] = value
                break
    return kept.drop(labels=["_score", "_length"])


def drop_mutual_duplicates(data: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    rows = [
        keep_mutual_accident(group) if len(group) > 1 else group.iloc[0]
        for _, group in data.groupby("numero_incidencia", sort=False)
    ]
    cleaned = pd.DataFrame(rows).reset_index(drop=True)
    return cleaned, len(data) - len(cleaned)


def format_fields(data: pd.DataFrame) -> dict[str, int]:
    """Normaliza fecha, hora y categorías. Devuelve cuántos valores cambian."""
    stats: dict[str, int] = {}
    incident_date = pd.to_datetime(data["numero_incidencia"].str.slice(0, 8), format="%Y%m%d")
    fecha = incident_date.dt.strftime("%Y-%m-%d")
    raw_date = data["fecha"].astype(str).str.replace(r"\s+0:00$", "", regex=True)
    parsed = pd.to_datetime(raw_date, format="%d/%m/%Y", errors="coerce")
    parsed = parsed.fillna(pd.to_datetime(raw_date, format="%Y-%m-%d", errors="coerce"))
    month_first = pd.to_datetime(raw_date, format="%m/%d/%Y", errors="coerce")
    swap = parsed.notna() & (parsed != incident_date) & month_first.eq(incident_date)
    parsed = parsed.where(~swap, month_first)
    stats["fechas_corregidas_con_el_id"] = int((parsed != incident_date).fillna(True).sum())
    data["fecha"] = fecha

    padded = data["hora"].map(lambda value: "{:02d}:{:02d}:{:02d}".format(*map(int, str(value).split(":"))))
    hora = pd.to_datetime(padded, format="%H:%M:%S")
    data["hora"] = hora.dt.strftime("%H:%M:%S")
    data["hora_decimal"] = (hora.dt.hour + hora.dt.minute / 60 + hora.dt.second / 3600).round(4)

    via = data["tipo_via"].map(lambda value: TIPO_VIA.get(_fold(str(value)), value) if _filled(value) else value)
    stats["tipo_via"] = int((via != data["tipo_via"]).sum())
    data["tipo_via"] = via

    def firme(value: object) -> object:
        if not _filled(value):
            return pd.NA
        return ESTADO_FIRME.get(_fold(str(value)), pd.NA if _fold(str(value)) == "(en blanco)" else value)

    nuevo_firme = data["estado_firme"].map(firme)
    stats["estado_firme"] = int((nuevo_firme.fillna("") != data["estado_firme"].fillna("")).sum())
    data["estado_firme"] = nuevo_firme

    def circulacion(value: object) -> object:
        if not _filled(value) or str(value) in {"0", "_"}:
            return pd.NA
        return str(value).strip().upper()

    nueva = data["circulacion"].map(circulacion)
    stats["circulacion"] = int((nueva.fillna("") != data["circulacion"].fillna("")).sum())
    data["circulacion"] = nueva

    carretera = data["carretera"].replace({"M607": "M-607"})
    stats["carretera"] = int((carretera.fillna("") != data["carretera"].fillna("")).sum())
    data["carretera"] = carretera

    data["unidad_samur_id"] = data["unidad_samur_id"].astype("Int64")
    data["grave"] = ((data["heridos_graves"] > 0) | (data["victimas_mortales"] > 0)).astype(int)
    return stats


def _canonical_label(value: str) -> str | None:
    return LABELS.get(_fold(value))


def _message_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return str(content)
    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text") or "")
    return "".join(parts)


def _parse_labels(raw: str) -> dict[str, str]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end <= start:
        raise ValueError(f"El clasificador no devolvió una lista JSON: {text[:240]}")
    payload = json.loads(text[start : end + 1])
    labels: dict[str, str] = {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        incident = str(item.get("numero_incidencia") or "")
        label = _canonical_label(str(item.get("tipo_colision") or ""))
        if incident and label:
            labels[incident] = label
    return labels


def _load_cache() -> dict[str, dict[str, str]]:
    if not CACHE.exists():
        return {}
    return json.loads(CACHE.read_text(encoding="utf-8"))


def _save_cache(cache: dict[str, dict[str, str]]) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def infer_tipo_colision(data: pd.DataFrame) -> int:
    """Rellena tipo_colision vacío leyendo la descripción. Devuelve cuántos rellena."""
    missing = data.index[data["tipo_colision"].isna() & data["descripcion"].map(_filled)]
    if len(missing) == 0:
        data["tipo_colision_inferido"] = False
        return 0

    cache = _load_cache()
    pending: list[tuple[object, str, str]] = []
    filled = 0
    inferred = pd.Series(False, index=data.index)
    for index in missing:
        incident = str(data.at[index, "numero_incidencia"])
        description = str(data.at[index, "descripcion"])
        cached = cache.get(incident)
        if cached and cached.get("descripcion") == description and _canonical_label(cached.get("tipo_colision", "")):
            data.at[index, "tipo_colision"] = _canonical_label(cached["tipo_colision"])
            inferred.at[index] = True
            filled += 1
        else:
            pending.append((index, incident, description))

    if not pending:
        data["tipo_colision_inferido"] = inferred
        return filled

    load_dotenv(ROOT / ".env")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("Falta ANTHROPIC_API_KEY en el entorno o en el fichero .env")

    model = ChatAnthropic(model="claude-sonnet-4-6", temperature=0, max_tokens=4000)
    for start in range(0, len(pending), 15):
        batch = pending[start : start + 15]
        lines = []
        for _, incident, description in batch:
            accident = data.loc[data["numero_incidencia"] == incident, "tipo_accidente"].iloc[0]
            lines.append(
                f"numero_incidencia: {incident}\n"
                f"tipo_accidente: {accident}\n"
                f"descripcion: {description}"
            )
        response = model.invoke(
            [
                SystemMessage(content=CLASSIFIER_PROMPT),
                HumanMessage(content="Clasifica estos informes:\n\n" + "\n\n".join(lines)),
            ]
        )
        labels = _parse_labels(_message_text(response.content))
        for index, incident, description in batch:
            label = labels.get(incident)
            if not label:
                continue
            data.at[index, "tipo_colision"] = label
            inferred.at[index] = True
            cache[incident] = {"descripcion": description, "tipo_colision": label}
            filled += 1
        _save_cache(cache)

    data["tipo_colision_inferido"] = inferred
    return filled


def column_order(data: pd.DataFrame) -> pd.DataFrame:
    original = [
        "fecha",
        "hora",
        "numero_incidencia",
        "localizacion",
        "ubicacion",
        "carretera",
        "eje",
        "tipo_via",
        "tipo_accidente",
        "tipo_colision",
        "vehiculos_implicados",
        "motos_implicadas",
        "pesados_implicados",
        "estado_firme",
        "circulacion",
        "heridos_leves",
        "heridos_graves",
        "victimas_mortales",
        "descripcion",
        "distrito",
        "unidad_samur_id",
    ]
    extra = ["hora_decimal", "grave", "tipo_colision_inferido"]
    return data[original + extra]


def main() -> None:
    raw = load_raw()
    blank_collision = int(raw["tipo_colision"].isna().sum())
    cleaned, removed = drop_mutual_duplicates(raw)
    blank_after_dedup = int(cleaned["tipo_colision"].isna().sum())
    stats = format_fields(cleaned)
    inferred = infer_tipo_colision(cleaned)
    still_blank = int(cleaned["tipo_colision"].isna().sum())
    without_text = int((cleaned["tipo_colision"].isna() & ~cleaned["descripcion"].map(_filled)).sum())
    output = column_order(cleaned)
    output.to_csv(TARGET, index=False)

    print(f"Origen: {len(raw)} filas en {SOURCE.name}")
    print(f"Duplicados mutuos eliminados: {removed}")
    print(f"Fechas que no coincidían con el número de incidencia y se corrigieron: {stats['fechas_corregidas_con_el_id']}")
    print(f"tipo_via unificados: {stats['tipo_via']}")
    print(f"estado_firme unificados o vaciados: {stats['estado_firme']}")
    print(f"circulacion unificadas o vaciadas: {stats['circulacion']}")
    print(f"carretera unificadas: {stats['carretera']}")
    print(f"tipo_colision vacíos al inicio: {blank_collision}; tras quitar duplicados: {blank_after_dedup}")
    print(f"tipo_colision inferidos desde la descripción: {inferred}")
    print(f"tipo_colision que siguen vacíos (sin descripción): {without_text}")
    print(f"Salida: {len(output)} filas, tipo_colision vacío {still_blank}, grave {int(output['grave'].sum())}")
    print(f"Escrito en {TARGET}")


if __name__ == "__main__":
    main()
