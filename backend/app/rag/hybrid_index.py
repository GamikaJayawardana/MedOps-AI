from pinecone import ServerlessSpec

from app.rag.index_setup import get_pinecone

HYBRID_INDEX_NAME = "medops-sops-hybrid"
EMBEDDING_DIM = 1024
METRIC = "dotproduct"        # REQUIRED for dense + sparse hybrid


def ensure_hybrid_index() -> None:
    """Create the hybrid (dense + sparse) index if it doesn't exist."""
    pc = get_pinecone()

    existing = [idx["name"] for idx in pc.list_indexes()]
    if HYBRID_INDEX_NAME in existing:
        print(f"Hybrid index '{HYBRID_INDEX_NAME}' already exists.")
        return

    print(f"Creating hybrid index '{HYBRID_INDEX_NAME}'...")
    pc.create_index(
        name=HYBRID_INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric=METRIC,
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    print("Hybrid index created.")


if __name__ == "__main__":
    ensure_hybrid_index()