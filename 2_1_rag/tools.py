from embeddings import get_vector_store

vector_store = get_vector_store()


def buscar_descripciones(pregunta: str, k: int = 5) -> str:
    """Busca informes de accidentes por significado.

    Úsala para preguntas sobre qué ocurrió, heridos, hospitales, distritos
    o cualquier detalle narrado en la descripción. No sirve para contar filas.

    Args:
        pregunta: Texto de la consulta, en lenguaje natural.
        k: Número de informes a devolver.
    """
    hits = vector_store.similarity_search(pregunta, k=k)
    if not hits:
        return "No hay informes que coincidan."
    bloques = []
    for doc in hits:
        meta = doc.metadata
        bloques.append(
            f"[{meta.get('numero_incidencia')} | {meta.get('distrito')} | {meta.get('fecha')}]\n"
            f"{doc.page_content}"
        )
    return "\n\n".join(bloques)
