from app.rag.embedder import embed_query
from app.rag.sparse import fit_bm25, encode_query
from app.rag.index_setup import get_pinecone
from app.rag.hybrid_index import HYBRID_INDEX_NAME

# BM25 must be fitted before we can encode queries.
fit_bm25()


def hybrid_search(query: str, top_k: int = 10) -> list[dict]:
    """Search using BOTH dense (meaning) and sparse (keyword) vectors."""
    pc = get_pinecone()
    index = pc.Index(HYBRID_INDEX_NAME)

    dense_vec = embed_query(query)       # meaning vector
    sparse_vec = encode_query(query)     # keyword vector

    results = index.query(
        vector=dense_vec,
        sparse_vector=sparse_vec,
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
