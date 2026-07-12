from app.rag.hybrid_retriever import hybrid_search
from app.rag.reranker import rerank


def retrieve_sops(query: str, top_n: int = 3) -> list[dict]:
    """Full pipeline: hybrid search -> re-rank -> best results."""
    candidates = hybrid_search(query, top_k=10)
    best = rerank(query, candidates, top_n=top_n)
    return best