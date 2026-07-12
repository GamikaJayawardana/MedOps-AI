from app.rag.embedder import embed_query
from app.rag.index_setup import get_pinecone, INDEX_NAME


def search_sops(query: str, top_k: int = 3) -> list[dict]:
    """Return the top_k most semantically similar SOPs to the query."""
    pc = get_pinecone()
    index = pc.Index(INDEX_NAME)

    query_vector = embed_query(query)

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
    )

    hits = []
    for match in results["matches"]:
        hits.append({
            "id": match["id"],
            "score": match["score"],
            "code": match["metadata"].get("code"),
            "text": match["metadata"].get("text"),
        })
    return hits