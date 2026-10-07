import pandas as pd
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

# Load the data
data = pd.read_csv("../data/accidentes.csv")

# Create the embeddings
embeddings = HuggingFaceEmbeddings(
    model="Qwen/Qwen3-Embedding-0.6B",
    show_progress=True,
    encode_kwargs={"normalize_embeddings": True},
    query_encode_kwargs={
        "normalize_embeddings": True,
        "prompt_name": "query",
    },
)

# Create docs
docs = [
    Document(
        id=str(row.numero_incidencia),
        page_content=row.descripcion.strip(),
        metadata={
            "numero_incidencia": row.numero_incidencia,
            "distrito": row.distrito,
            "fecha": row.fecha,
        },
    )
    for row in data.itertuples()
    if isinstance(row.descripcion, str) and row.descripcion.strip()
]

# Load vector store with embeddings model
vector_store = InMemoryVectorStore(embeddings)
ids = vector_store.add_documents(docs)



