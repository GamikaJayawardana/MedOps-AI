from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

print(f"Loading re-ranker '{MODEL_NAME}' (small, first run downloads)...")
_reranker = CrossEncoder(MODEL_NAME)
print("Re-ranker loaded.")


def rerank(query: str, hits: list[dict], top_n: int = 3) -> list[dict]:
    """Re-score hits by reading query + document together, return best top_n."""
    if not hits:
        return []

    # Make (query, document_text) pairs for the model to score.
    pairs = [(query, h["text"]) for h in hits]
    scores = _reranker.predict(pairs)

    # Attach the new score to each hit.
    for hit, score in zip(hits, scores):
        hit["rerank_score"] = float(score)

    # Sort by the new score, highest first, keep top_n.
    reranked = sorted(hits, key=lambda h: h["rerank_score"], reverse=True)
    return reranked[:top_n]