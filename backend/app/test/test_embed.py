from app.rag.embedder import embed_query

vec = embed_query("respiratory ward is overflowing")
print(f"Vector length: {len(vec)}")
print(f"First 5 numbers: {vec[:5]}")