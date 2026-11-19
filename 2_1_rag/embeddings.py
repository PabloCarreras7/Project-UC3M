"""Sube los partes de accidentes a Pinecone. Se ejecuta una sola vez.

Cada fila de accidentes_clean.csv es un vector. El texto que se codifica es un
resumen de los campos del parte seguido de la descripción; el resto de columnas
viaja como metadatos para poder filtrar.

    python embeddings.py
    python embeddings.py --force
"""

import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

INDEX_NAME = os.environ.get("PINECONE_INDEX", "accidentes-descripcion")
EMBEDDING_DIM = 1024
SIN_DESCRIPCION = "Sin descripción."
_embeddings: HuggingFaceEmbeddings | None = None

# Columnas que se guardan como metadatos, con su tipo en Pinecone.
TEXT_FIELDS = (
    "fecha",
    "hora",
    "localizacion",
    "ubicacion",
    "carretera",
    "eje",
    "tipo_via",
    "tipo_accidente",
    "tipo_colision",
    "estado_firme",
    "circulacion",
    "distrito",
)
INT_FIELDS = (
    "vehiculos_implicados",
    "motos_implicadas",
    "pesados_implicados",
    "heridos_leves",
    "heridos_graves",
    "victimas_mortales",
    "unidad_samur_id",
)
BOOL_FIELDS = ("grave", "tipo_colision_inferido", "fuera_de_madrid")


def require_pinecone_key() -> str:
    key = os.environ.get("PINECONE_API_KEY")
    if not key:
        raise RuntimeError("Falta PINECONE_API_KEY en el fichero .env")
    return key


def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model="Qwen/Qwen3-Embedding-0.6B",
            show_progress=True,
            encode_kwargs={"normalize_embeddings": True},
            query_encode_kwargs={
                "normalize_embeddings": True,
                "prompt_name": "query",
            },
        )
    return _embeddings


def load_rows() -> pd.DataFrame:
    data = pd.read_csv(ROOT / "data_clean" / "accidentes_clean.csv")
    return data.drop_duplicates("numero_incidencia")


def _plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


def row_summary(row: dict) -> str:
    """Resume en una o dos frases los campos del parte que tienen significado."""

    def has(field: str) -> bool:
        return pd.notna(row.get(field))

    accidente = str(row["tipo_accidente"]).lower()
    if has("tipo_colision") and row["tipo_colision"] != "Otro":
        accidente += f" ({str(row['tipo_colision']).lower()})"
    lugar = []
    if has("carretera"):
        lugar.append(f"en la {row['carretera']}")
    lugar.append(str(row["tipo_via"]).lower())
    lugar.append("en túnel" if row["ubicacion"] == "TÚNEL" else "en superficie")
    lugar.append(f"distrito {str(row['distrito']).title()}")
    frases = [f"{accidente.capitalize()} {', '.join(lugar)}."]

    if has("vehiculos_implicados"):
        vehiculos = _plural(
            int(row["vehiculos_implicados"]), "vehículo implicado", "vehículos implicados"
        )
        extra = []
        if row["motos_implicadas"]:
            extra.append(_plural(int(row["motos_implicadas"]), "moto", "motos"))
        if row["pesados_implicados"]:
            extra.append(
                _plural(int(row["pesados_implicados"]), "vehículo pesado", "vehículos pesados")
            )
        frases.append(f"{vehiculos}{f' ({', '.join(extra)})' if extra else ''}.")

    entorno = []
    if has("estado_firme") and row["estado_firme"] != "Otros":
        entorno.append(f"firme {str(row['estado_firme']).lower()}")
    if has("circulacion"):
        entorno.append(f"circulación {str(row['circulacion']).lower()}")
    if entorno:
        frases.append(f"{', '.join(entorno).capitalize()}.")

    victimas = []
    if has("heridos_leves") and row["heridos_leves"]:
        victimas.append(_plural(int(row["heridos_leves"]), "herido leve", "heridos leves"))
    if row["heridos_graves"]:
        victimas.append(_plural(int(row["heridos_graves"]), "herido grave", "heridos graves"))
    if row["victimas_mortales"]:
        victimas.append(
            _plural(int(row["victimas_mortales"]), "víctima mortal", "víctimas mortales")
        )
    if victimas:
        frases.append(f"{', '.join(victimas).capitalize()}.")
    elif has("heridos_leves"):
        frases.append("Sin heridos.")
    return " ".join(frases)


def row_metadata(row: dict) -> dict:
    """Metadatos tipados. Pinecone no admite nulos: los campos vacíos se omiten."""
    meta: dict = {"numero_incidencia": str(row["numero_incidencia"])}
    for field in TEXT_FIELDS:
        if pd.notna(row.get(field)):
            meta[field] = str(row[field])
    for field in INT_FIELDS:
        if pd.notna(row.get(field)):
            meta[field] = int(row[field])
    for field in BOOL_FIELDS:
        meta[field] = bool(row[field])
    # Pinecone solo compara rangos con números: la fecha va también como AAAAMMDD.
    meta["fecha_num"] = int(str(row["fecha"]).replace("-", ""))
    meta["hora_decimal"] = float(row["hora_decimal"])
    meta["tiene_descripcion"] = isinstance(row.get("descripcion"), str) and bool(
        row["descripcion"].strip()
    )
    return meta


def load_documents() -> list[Document]:
    docs = []
    for row in load_rows().to_dict("records"):
        meta = row_metadata(row)
        descripcion = row["descripcion"].strip() if meta["tiene_descripcion"] else SIN_DESCRIPCION
        docs.append(
            Document(
                id=meta["numero_incidencia"],
                page_content=f"{row_summary(row)}\nDescripción: {descripcion}",
                metadata=meta,
            )
        )
    return docs


def pinecone_client() -> Pinecone:
    return Pinecone(api_key=require_pinecone_key())


def ensure_index() -> object:
    client = pinecone_client()
    if not client.has_index(INDEX_NAME):
        client.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=os.environ.get("PINECONE_CLOUD", "aws"),
                region=os.environ.get("PINECONE_REGION", "eu-west-1"),
            ),
        )
        while not client.describe_index(INDEX_NAME).status["ready"]:
            time.sleep(1)
    return client.Index(INDEX_NAME)


def vector_count(index: object) -> int:
    stats = index.describe_index_stats()
    total = stats.get("total_vector_count") if isinstance(stats, dict) else stats.total_vector_count
    return int(total or 0)


def get_vector_store() -> PineconeVectorStore:
    client = pinecone_client()
    if not client.has_index(INDEX_NAME):
        raise RuntimeError(
            f"No existe el índice {INDEX_NAME}. Ejecuta primero: python embeddings.py"
        )
    return PineconeVectorStore(index=client.Index(INDEX_NAME), embedding=get_embeddings())


def index_descriptions(force: bool = False) -> None:
    index = ensure_index()
    count = vector_count(index)
    if count and not force:
        print(f"El índice {INDEX_NAME} ya tiene {count} vectores. No se vuelve a indexar.")
        print("Usa python embeddings.py --force para rehacerlo.")
        return
    docs = load_documents()
    store = PineconeVectorStore(index=index, embedding=get_embeddings())
    # El id es el número de incidencia: al rehacer, cada vector sustituye al anterior.
    # Subida síncrona y en tandas cortas: una petición colgada falla en vez de bloquear.
    store.add_documents(
        docs,
        ids=[doc.id for doc in docs],
        embedding_chunk_size=200,
        batch_size=100,
        async_req=False,
    )
    print(f"Indexados {len(docs)} partes en {INDEX_NAME}.")


if __name__ == "__main__":
    import sys

    index_descriptions(force="--force" in sys.argv)
