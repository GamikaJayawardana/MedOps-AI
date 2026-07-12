from app.rag.embedder import embed_texts
from app.rag.sparse import fit_bm25, encode_documents
from app.rag.ingest import load_sops
from app.rag.index_setup import get_pinecone
from app.rag.hybrid_index import ensure_hybrid_index, HYBRID_INDEX_NAME


def hybrid_ingest() -> None:
    ensure_hybrid_index()
    pc = get_pinecone()
    index = pc.Index(HYBRID_INDEX_NAME)

    docs = load_sops()
    texts = [d["text"] for d in docs]
    print(f"Loaded {len(docs)} SOP documents.")

    # 1. Dense vectors (meaning) from bge-m3.
    dense_vectors = embed_texts(texts)
    print(f"Made {len(dense_vectors)} dense vectors.")

    # 2. Sparse vectors (keywords) from BM25 — must fit first.
    fit_bm25()
    sparse_vectors = encode_documents(texts)
    print(f"Made {len(sparse_vectors)} sparse vectors.")

    # 3. Build payload with BOTH vectors per document.
    to_upsert = []
    for doc, dense, sparse in zip(docs, dense_vectors, sparse_vectors):
        to_upsert.append({
            "id": doc["id"],
            "values": dense,                 # dense vector
            "sparse_values": sparse,         # sparse vector
            "metadata": doc["metadata"],
        })

    index.upsert(vectors=to_upsert)
    print(f"Upserted {len(to_upsert)} hybrid vectors to '{HYBRID_INDEX_NAME}'.")


if __name__ == "__main__":
    hybrid_ingest()