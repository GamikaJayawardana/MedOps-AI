from pinecone_text.sparse import BM25Encoder 

from app.rag.ingest import load_sops

# One BM25 encoder for the whole app.
_bm25 = BM25Encoder()
_is_fitted = False


def fit_bm25() -> BM25Encoder:
    """Teach BM25 the words in our SOP documents (run once)."""
    global _is_fitted
    docs = load_sops()
    texts = [d["text"] for d in docs]
    _bm25.fit(texts)          # BM25 reads all documents and learns the words
    _is_fitted = True
    print(f"BM25 fitted on {len(texts)} documents.")
    return _bm25


def encode_documents(texts: list[str]) -> list[dict]:
    """Make sparse vectors for documents (for storing)."""
    return _bm25.encode_documents(texts)


def encode_query(text: str) -> dict:
    """Make one sparse vector for a query (for searching)."""
    return _bm25.encode_queries([text])[0]