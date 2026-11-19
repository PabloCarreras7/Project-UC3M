import unicodedata

from embeddings import get_vector_store, load_rows

vector_store = get_vector_store()

MAX_K = 20
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
_rows = load_rows()
VOCAB = {field: sorted(_rows[field].dropna().unique()) for field in CATEGORY_FILTERS}
del _rows


def _key(text: str) -> str:
    """Compara sin mayúsculas, tildes ni espacios o puntos."""
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return "".join(ch for ch in plain.lower() if ch.isalnum())


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


def _format(doc) -> str:
    # Pinecone devuelve los enteros como float: 1.0 vuelve a ser 1.
    meta = {
        key: int(value) if isinstance(value, float) and value.is_integer() else value
        for key, value in doc.metadata.items()
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
    return f"[{' | '.join(cabecera)}]\n{' · '.join(datos)}\n{doc.page_content}"


def buscar_descripciones(
    pregunta: str,
    k: int = 5,
    distrito: str | None = None,
    carretera: str | None = None,
    tipo_accidente: str | None = None,
    tipo_colision: str | None = None,
    ubicacion: str | None = None,
    tipo_via: str | None = None,
    estado_firme: str | None = None,
    circulacion: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    solo_graves: bool = False,
    con_heridos: bool = False,
    con_motos: bool = False,
    con_pesados: bool = False,
) -> str:
    """Busca partes de accidentes por significado y devuelve la fila completa de cada uno.

    La búsqueda compara la pregunta con un resumen del parte más su descripción.
    Los filtros son exactos: úsalos cuando la pregunta fije un distrito, una carretera,
    unas fechas o la gravedad, en vez de confiar en el parecido del texto.
    No sirve para contar filas: solo devuelve los k partes más parecidos.

    Args:
        pregunta: Texto de la consulta, en lenguaje natural.
        k: Número de partes a devolver (máximo 20).
        distrito: Distrito, por ejemplo TETUAN, CENTRO o SAN BLAS. Si no existe, se devuelve la lista válida.
        carretera: M30, A1, A2, A3, A4, A42, A5, M11, M23, M500, M607 o AV.ANDALUCIA.
        tipo_accidente: Colision entre vehiculos, Salida de via, Vuelco, Colisión obstáculo, Atropello u Otros.
        tipo_colision: COLISIÓN POR ALCANCE, COLISIÓN LATERAL, COLISIÓN MEDIANA, COLISIÓN FRONTAL u Otro.
        ubicacion: SUPERFICIE o TÚNEL.
        tipo_via: TRONCO, VIA DE SERVICIO, RAMAL, TRANSFER, TUNEL o TABLERO.
        estado_firme: Seco y limpio, Mojado, Húmedo u Otros.
        circulacion: FLUIDA, DENSA o CONGESTIONADA.
        fecha_desde: Primera fecha admitida, AAAA-MM-DD. Los datos son de 2024.
        fecha_hasta: Última fecha admitida, AAAA-MM-DD.
        solo_graves: True para partes con heridos graves o víctimas mortales.
        con_heridos: True para partes con algún herido o víctima mortal.
        con_motos: True para partes con motos implicadas.
        con_pesados: True para partes con vehículos pesados implicados.
    """
    clauses: list[dict] = []
    categorias = {
        "distrito": distrito,
        "carretera": carretera,
        "tipo_accidente": tipo_accidente,
        "tipo_colision": tipo_colision,
        "ubicacion": ubicacion,
        "tipo_via": tipo_via,
        "estado_firme": estado_firme,
        "circulacion": circulacion,
    }
    for field, value in categorias.items():
        if not value:
            continue
        option = _match(field, value)
        if option is None:
            return (
                f"El valor «{value}» no existe en {field}. "
                f"Valores válidos: {', '.join(VOCAB[field])}."
            )
        clauses.append({field: {"$eq": option}})

    for name, value, op in (
        ("fecha_desde", fecha_desde, "$gte"),
        ("fecha_hasta", fecha_hasta, "$lte"),
    ):
        if not value:
            continue
        number = _fecha_num(value)
        if number is None:
            return f"{name} debe tener el formato AAAA-MM-DD; se recibió «{value}»."
        clauses.append({"fecha_num": {op: number}})

    if solo_graves:
        clauses.append({"grave": {"$eq": True}})
    if con_heridos:
        clauses.append(
            {
                "$or": [
                    {"heridos_leves": {"$gt": 0}},
                    {"heridos_graves": {"$gt": 0}},
                    {"victimas_mortales": {"$gt": 0}},
                ]
            }
        )
    if con_motos:
        clauses.append({"motos_implicadas": {"$gt": 0}})
    if con_pesados:
        clauses.append({"pesados_implicados": {"$gt": 0}})

    filtro = {"$and": clauses} if clauses else None
    hits = vector_store.similarity_search(pregunta, k=max(1, min(k, MAX_K)), filter=filtro)
    if not hits:
        return "No hay partes que coincidan con la búsqueda y los filtros."
    return "\n\n".join(_format(doc) for doc in hits)
