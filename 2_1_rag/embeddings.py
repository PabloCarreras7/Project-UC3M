"""Sube las descripciones de accidentes a Pinecone. Se ejecuta una sola vez.

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
_embeddings: HuggingFaceEmbeddings | None = None


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


def load_documents() -> list[Document]:
    data = pd.read_csv(ROOT / "data_clean" / "accidentes_clean.csv")
    docs = []
    seen: set[str] = set()
    for row in data.itertuples():
        text = row.descripcion.strip() if isinstance(row.descripcion, str) else ""
        if not text:
            continue
        doc_id = str(row.numero_incidencia)
        if doc_id in seen:
            continue
        seen.add(doc_id)
        docs.append(
            Document(
                id=doc_id,
                page_content=text,
                metadata={
                    "numero_incidencia": doc_id,
                    "distrito": str(row.distrito),
                    "fecha": str(row.fecha),
                },
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
    store.add_documents(docs, ids=[doc.id for doc in docs])
    print(f"Indexados {len(docs)} informes en {INDEX_NAME}.")


if __name__ == "__main__":
    import sys

    index_descriptions(force="--force" in sys.argv)
