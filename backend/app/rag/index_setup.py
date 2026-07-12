from pinecone import Pinecone, ServerlessSpec

from app.config import settings

INDEX_NAME = "medops-sops"
EMBEDDING_DIM = 1024        # bge-m3 outputs 1024-dimensional vectors
METRIC = "cosine"


def get_pinecone() -> Pinecone:
    """Return an authenticated Pinecone client."""
    return Pinecone(api_key=settings.pinecone_api_key.get_secret_value())


def ensure_index() -> None:
    """Create the SOP index if it doesn't already exist."""
    pc = get_pinecone()

    existing = [idx["name"] for idx in pc.list_indexes()]
    if INDEX_NAME in existing:
        print(f"Index '{INDEX_NAME}' already exists — nothing to do.")
        return

    print(f"Creating index '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric=METRIC,
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    print("Index created.")


if __name__ == "__main__":
    ensure_index()