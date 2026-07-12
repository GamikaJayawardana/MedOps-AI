from pathlib import Path

from app.rag.embedder import embed_texts
from app.rag.index_setup import get_pinecone, ensure_index, INDEX_NAME

SOPS_DIR = Path(__file__).parent / "sops"


def parse_filename(filename: str) -> dict:
    """Turn 'SOP-RESP-01-overflow.txt' into structured metadata."""
    stem = filename.replace(".txt", "")          # SOP-RESP-01-overflow
    parts = stem.split("-")                        # ['SOP', 'RESP', '01', 'overflow']
    ward_map = {
        "RESP": "respiratory", "CARD": "cardiology",
        "GEN": "general", "PED": "pediatric", "ALL": "all",
    }
    return {
        "id": stem,                                # SOP-RESP-01-overflow
        "ward": ward_map.get(parts[1], "unknown"),
        "code": f"{parts[1]}-{parts[2]}",          # RESP-01
        "category": parts[3],                      # overflow
    }


def load_sops() -> list[dict]:
    """Read every .txt in the sops folder into a list of docs."""
    docs = []
    for path in sorted(SOPS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        meta = parse_filename(path.name)
        meta["text"] = text                        # keep text in metadata too
        docs.append({"id": meta["id"], "text": text, "metadata": meta})
    return docs


def ingest() -> None:
    ensure_index()
    pc = get_pinecone()
    index = pc.Index(INDEX_NAME)

    docs = load_sops()
    print(f"Loaded {len(docs)} SOP documents.")

    texts = [d["text"] for d in docs]
    vectors = embed_texts(texts)
    print(f"Embedded {len(vectors)} documents.")

    # Build the payload Pinecone expects: (id, vector, metadata) per doc.
    to_upsert = [
        {"id": d["id"], "values": vec, "metadata": d["metadata"]}
        for d, vec in zip(docs, vectors)
    ]

    index.upsert(vectors=to_upsert)
    print(f"Upserted {len(to_upsert)} vectors to '{INDEX_NAME}'.")


if __name__ == "__main__":
    ingest()