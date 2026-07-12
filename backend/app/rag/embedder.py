from sentence_transformers import SentenceTransformer  # type: ignore
MODEL_NAME = "BAAI/bge-m3"

# Load the model ONCE at import time and reuse it.
# The first time this runs, it downloads ~2GB from HuggingFace.
print(f"Loading embedding model '{MODEL_NAME}' (first run downloads ~2GB)...")
_model = SentenceTransformer(MODEL_NAME)
print("Embedding model loaded.")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Turn a list of texts into a list of 1024-dim vectors."""
    embeddings = _model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(text: str) -> list[float]:
    """Embed a single query string, return one vector."""
    return embed_texts([text])[0]