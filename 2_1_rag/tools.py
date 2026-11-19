"""Herramientas del agente: búsqueda por significado, recuento y listado exactos.

buscar_descripciones consulta Pinecone. contar_partes y listar_partes leen
accidentes_clean.csv con pandas, porque un total solo es fiable sobre todas las filas.
Las tres comparten los mismos filtros.
"""

import unicodedata
from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field

from embeddings import SIN_DESCRIPCION, get_vector_store, load_rows, row_metadata, row_summary

vector_store = get_vector_store()

MAX_K = 20
MAX_LISTA = 50
# Filtros de valor exacto y los valores que admite cada uno, leídos del CSV.
CATEGORY_FILTERS = (
    "distrito",
    "carretera",
    "tipo_accidente",
    "tipo_colision",
    "ubicacion",
    "tipo_via",
    "estado_firme",
    "circulacion",
)
DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
SUMAS = {
    "heridos_leves": "heridos leves",
    "heridos_graves": "heridos graves",
    "victimas_mortales": "víctimas mortales",
    "grave": "partes graves",
}


def _key(text: str) -> str:
    """Compara sin mayúsculas, tildes ni espacios o puntos."""
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return "".join(ch for ch in plain.lower() if ch.isalnum())


def _plain(text: str) -> str:
    """Minúsculas, sin tildes y con un solo espacio entre palabras."""
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return " ".join(plain.lower().split())


DATA = load_rows().reset_index(drop=True)
VOCAB = {field: sorted(DATA[field].dropna().unique()) for field in CATEGORY_FILTERS}
DATA["fecha_num"] = DATA["fecha"].str.replace("-", "").astype(int)
DATA["mes"] = DATA["fecha"].str.slice(0, 7)
DATA["dia_semana"] = pd.to_datetime(DATA["fecha"]).dt.dayofweek.map(lambda day: DIAS[day])
DATA["hora_del_dia"] = DATA["hora_decimal"].astype(int)
DATA["_texto"] = DATA["descripcion"].fillna("").map(_plain)


class Filtros(BaseModel):
    """Condiciones exactas sobre los campos del parte. Son opcionales y se cumplen todas a la vez."""

    distrito: str | None = Field(
        None, description="Distrito, por ejemplo TETUAN, CENTRO o SAN BLAS."
    )
    carretera: str | None = Field(
        None,
        description="M30, A1, A2, A3, A4, A42, A5, M11, M23, M500, M607 o AV.ANDALUCIA.",
    )
    tipo_accidente: str | None = Field(
        None,
        description="Colision entre vehiculos, Salida de via, Vuelco, Colisión obstáculo, Atropello u Otros.",
    )
    tipo_colision: str | None = Field(
        None,
        description="COLISIÓN POR ALCANCE, COLISIÓN LATERAL, COLISIÓN MEDIANA, COLISIÓN FRONTAL u Otro.",
    )
    ubicacion: str | None = Field(None, description="SUPERFICIE o TÚNEL.")
    tipo_via: str | None = Field(
        None, description="TRONCO, VIA DE SERVICIO, RAMAL, TRANSFER, TUNEL o TABLERO."
    )
    estado_firme: str | None = Field(None, description="Seco y limpio, Mojado, Húmedo u Otros.")
    circulacion: str | None = Field(None, description="FLUIDA, DENSA o CONGESTIONADA.")
    fecha_desde: str | None = Field(
        None, description="Primera fecha admitida, AAAA-MM-DD. Los datos son de 2024."
    )
    fecha_hasta: str | None = Field(None, description="Última fecha admitida, AAAA-MM-DD.")
    solo_graves: bool = Field(
        False, description="True para partes con heridos graves o víctimas mortales."
    )
    con_heridos: bool = Field(
        False, description="True para partes con algún herido o víctima mortal."
    )
    con_fallecidos: bool = Field(False, description="True para partes con víctimas mortales.")
    con_motos: bool = Field(False, description="True para partes con motos implicadas.")
    con_pesados: bool = Field(
        False, description="True para partes con vehículos pesados implicados."
    )


def _match(field: str, value: str) -> str | None:
    wanted = _key(value)
    for option in VOCAB[field]:
        if _key(option) == wanted:
            return option
    partial = [option for option in VOCAB[field] if wanted and wanted in _key(option)]
    return partial[0] if len(partial) == 1 else None


def _fecha_num(value: str) -> int | None:
    digits = value.strip().replace("-", "")
    return int(digits) if len(digits) == 8 and digits.isdigit() else None


def _resolve(filtros: Filtros | None) -> tuple[dict, str | None]:
    """Valida los filtros. Devuelve los valores ya normalizados o un mensaje de error."""
    filtros = filtros or Filtros()
    resolved: dict = {"categorias": {}, "desde": None, "hasta": None, "fuente": filtros}
    for field in CATEGORY_FILTERS:
        value = getattr(filtros, field)
        if not value:
            continue
        option = _match(field, value)
        if option is None:
            return resolved, (
                f"El valor «{value}» no existe en {field}. "
                f"Valores válidos: {', '.join(VOCAB[field])}."
            )
        resolved["categorias"][field] = option
    for name, target in (("fecha_desde", "desde"), ("fecha_hasta", "hasta")):
        value = getattr(filtros, name)
        if not value:
            continue
        number = _fecha_num(value)
        if number is None:
            return resolved, f"{name} debe tener el formato AAAA-MM-DD; se recibió «{value}»."
        resolved[target] = number
    return resolved, None


def _pinecone_filter(resolved: dict) -> dict | None:
    filtros: Filtros = resolved["fuente"]
    clauses: list[dict] = [
        {field: {"$eq": option}} for field, option in resolved["categorias"].items()
    ]
    if resolved["desde"] is not None:
        clauses.append({"fecha_num": {"$gte": resolved["desde"]}})
    if resolved["hasta"] is not None:
        clauses.append({"fecha_num": {"$lte": resolved["hasta"]}})
    if filtros.solo_graves:
        clauses.append({"grave": {"$eq": True}})
    if filtros.con_heridos:
        clauses.append(
            {
                "$or": [
                    {"heridos_leves": {"$gt": 0}},
                    {"heridos_graves": {"$gt": 0}},
                    {"victimas_mortales": {"$gt": 0}},
                ]
            }
        )
    if filtros.con_fallecidos:
        clauses.append({"victimas_mortales": {"$gt": 0}})
    if filtros.con_motos:
        clauses.append({"motos_implicadas": {"$gt": 0}})
    if filtros.con_pesados:
        clauses.append({"pesados_implicados": {"$gt": 0}})
    return {"$and": clauses} if clauses else None


def _select(resolved: dict, texto_contiene: list[str] | None) -> pd.DataFrame:
    """Filas del CSV que cumplen los filtros y contienen alguna de las expresiones."""
    filtros: Filtros = resolved["fuente"]
    mask = pd.Series(True, index=DATA.index)
    for field, option in resolved["categorias"].items():
        mask &= DATA[field] == option
    if resolved["desde"] is not None:
        mask &= DATA["fecha_num"] >= resolved["desde"]
    if resolved["hasta"] is not None:
        mask &= DATA["fecha_num"] <= resolved["hasta"]
    if filtros.solo_graves:
        mask &= DATA["grave"] == 1
    if filtros.con_heridos:
        mask &= (
            (DATA["heridos_leves"] > 0)
            | (DATA["heridos_graves"] > 0)
            | (DATA["victimas_mortales"] > 0)
        )
    if filtros.con_fallecidos:
        mask &= DATA["victimas_mortales"] > 0
    if filtros.con_motos:
        mask &= DATA["motos_implicadas"] > 0
    if filtros.con_pesados:
        mask &= DATA["pesados_implicados"] > 0
    terms = [_plain(term) for term in texto_contiene or [] if _plain(term)]
    if terms:
        found = pd.Series(False, index=DATA.index)
        for term in terms:
            found |= DATA["_texto"].str.contains(term, regex=False)
        mask &= found
    return DATA[mask]


def _applied(resolved: dict, texto_contiene: list[str] | None) -> str:
    """Describe los filtros que se han aplicado de verdad, para que el agente lo compruebe."""
    filtros: Filtros = resolved["fuente"]
    parts = [f"{field} = {option}" for field, option in resolved["categorias"].items()]
    if filtros.fecha_desde:
        parts.append(f"fecha desde {filtros.fecha_desde}")
    if filtros.fecha_hasta:
        parts.append(f"fecha hasta {filtros.fecha_hasta}")
    for flag, label in (
        ("solo_graves", "solo graves"),
        ("con_heridos", "con heridos"),
        ("con_fallecidos", "con víctimas mortales"),
        ("con_motos", "con motos"),
        ("con_pesados", "con pesados"),
    ):
        if getattr(filtros, flag):
            parts.append(label)
    terms = [term for term in texto_contiene or [] if _plain(term)]
    if terms:
        parts.append("la descripción contiene " + " o ".join(f"«{term}»" for term in terms))
    return "; ".join(parts) if parts else "ninguno (todos los partes)"


def _format(meta: dict, text: str) -> str:
    # Pinecone devuelve los enteros como float: 1.0 vuelve a ser 1.
    meta = {
        key: int(value) if isinstance(value, float) and value.is_integer() else value
        for key, value in meta.items()
    }
    cabecera = [
        str(meta.get("numero_incidencia")),
        f"{meta.get('fecha')} {meta.get('hora')}",
        str(meta.get("distrito")),
        f"{meta.get('carretera', 'sin carretera')} {meta.get('localizacion')}",
    ]
    datos = [
        f"vehículos: {meta.get('vehiculos_implicados', 'sin dato')}",
        f"motos: {meta.get('motos_implicadas')}",
        f"pesados: {meta.get('pesados_implicados')}",
        f"heridos leves: {meta.get('heridos_leves', 'sin dato')}",
        f"heridos graves: {meta.get('heridos_graves')}",
        f"víctimas mortales: {meta.get('victimas_mortales')}",
        f"grave: {'sí' if meta.get('grave') else 'no'}",
    ]
    if "unidad_samur_id" in meta:
        datos.append(f"unidad SAMUR: {meta['unidad_samur_id']}")
    return f"[{' | '.join(cabecera)}]\n{' · '.join(datos)}\n{text}"


def _format_row(row: dict) -> str:
    meta = row_metadata(row)
    descripcion = row["descripcion"].strip() if meta["tiene_descripcion"] else SIN_DESCRIPCION
    return _format(meta, f"{row_summary(row)}\nDescripción: {descripcion}")


def _sums(rows: pd.DataFrame) -> list[int]:
    return [int(rows[field].sum()) for field in SUMAS]


def buscar_descripciones(pregunta: str, k: int = 5, filtros: Filtros | None = None) -> str:
    """Busca partes de accidentes por significado y devuelve la fila completa de cada uno.

    La búsqueda compara la pregunta con un resumen del parte más su descripción.
    Úsala para saber qué ocurrió o cómo. Devuelve solo los k partes más parecidos:
    no sirve para contar ni para listar todos los que cumplen una condición.

    Args:
        pregunta: Texto de la consulta, en lenguaje natural.
        k: Número de partes a devolver (máximo 20).
        filtros: Condiciones exactas que deben cumplir los partes.
    """
    resolved, error = _resolve(filtros)
    if error:
        return error
    hits = vector_store.similarity_search(
        pregunta, k=max(1, min(k, MAX_K)), filter=_pinecone_filter(resolved)
    )
    if not hits:
        return "No hay partes que coincidan con la búsqueda y los filtros."
    return "\n\n".join(_format(doc.metadata, doc.page_content) for doc in hits)


def contar_partes(
    filtros: Filtros | None = None,
    texto_contiene: list[str] | None = None,
    agrupar_por: Literal[
        "distrito",
        "carretera",
        "tipo_accidente",
        "tipo_colision",
        "ubicacion",
        "tipo_via",
        "estado_firme",
        "circulacion",
        "mes",
        "dia_semana",
        "hora_del_dia",
    ]
    | None = None,
) -> str:
    """Cuenta de forma exacta los partes que cumplen unas condiciones, sobre todas las filas.

    Devuelve el número de partes y la suma de heridos leves, heridos graves,
    víctimas mortales y partes graves. Con agrupar_por añade el desglose por ese campo.
    Úsala siempre que pidan cuántos, totales, comparaciones o rankings.

    Args:
        filtros: Condiciones exactas que deben cumplir los partes.
        texto_contiene: Palabras o frases literales; cuenta los partes cuya descripción
            contiene alguna de ellas, sin distinguir mayúsculas ni tildes. Pasa las variantes
            de un mismo nombre, por ejemplo ["12 de octubre", "12 octubre", "doce de octubre"].
        agrupar_por: Campo por el que desglosar el recuento.
    """
    resolved, error = _resolve(filtros)
    if error:
        return error
    rows = _select(resolved, texto_contiene)
    total = _sums(rows)
    lines = [
        f"Filtros aplicados: {_applied(resolved, texto_contiene)}",
        f"Partes: {len(rows)} de {len(DATA)}",
        " · ".join(f"{label}: {value}" for label, value in zip(SUMAS.values(), total)),
    ]
    if agrupar_por and len(rows):
        groups = [
            (key, len(group), _sums(group))
            for key, group in rows.groupby(agrupar_por, dropna=False, sort=True)
        ]
        if agrupar_por == "dia_semana":
            groups.sort(key=lambda item: DIAS.index(item[0]))
        elif agrupar_por not in ("mes", "hora_del_dia"):
            groups.sort(key=lambda item: -item[1])
        lines.append("")
        lines.append(f"{agrupar_por} | partes | {' | '.join(SUMAS.values())}")
        for key, count, sums in groups:
            label = "sin dato" if pd.isna(key) else str(key)
            lines.append(f"{label} | {count} | {' | '.join(str(value) for value in sums)}")
    return "\n".join(lines)


def listar_partes(
    filtros: Filtros | None = None,
    texto_contiene: list[str] | None = None,
    limite: int = 20,
    recientes_primero: bool = False,
) -> str:
    """Lista todos los partes que cumplen unas condiciones, ordenados por fecha.

    No ordena por parecido: devuelve las filas que cumplen los filtros, completas.
    Úsala cuando pidan «todos los…» o cuando busquen un nombre o una palabra literal
    en la descripción (un hospital, una calle, una grúa).

    Args:
        filtros: Condiciones exactas que deben cumplir los partes.
        texto_contiene: Palabras o frases literales; lista los partes cuya descripción
            contiene alguna de ellas, sin distinguir mayúsculas ni tildes.
        limite: Número máximo de partes a devolver (máximo 50).
        recientes_primero: True para empezar por los más recientes.
    """
    resolved, error = _resolve(filtros)
    if error:
        return error
    rows = _select(resolved, texto_contiene).sort_values(
        ["fecha", "hora"], ascending=not recientes_primero
    )
    header = f"Filtros aplicados: {_applied(resolved, texto_contiene)}"
    if rows.empty:
        return f"{header}\nNingún parte cumple estas condiciones."
    shown = rows.head(max(1, min(limite, MAX_LISTA)))
    count = (
        f"{len(rows)} partes cumplen las condiciones; se muestran los {len(shown)} "
        f"{'más recientes' if recientes_primero else 'primeros'}."
        if len(shown) < len(rows)
        else f"{len(rows)} partes cumplen las condiciones; se muestran todos."
    )
    blocks = [_format_row(row) for row in shown.to_dict("records")]
    return "\n\n".join([f"{header}\n{count}", *blocks])


TOOLS = [buscar_descripciones, contar_partes, listar_partes]
