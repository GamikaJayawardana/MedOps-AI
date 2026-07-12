from app.rag.retriever import search_sops

queries = [
    "the respiratory ward is overflowing, what should we do?",
    "we are running out of ventilators",
    "how many hours can staff work?",
    "Protocol 4B",   # exact code — watch how semantic search handles this
]

for q in queries:
    print(f"\n=== QUERY: {q} ===")
    hits = search_sops(q, top_k=3)
    for h in hits:
        preview = h["text"][:70] + "..."
        print(f"  [{h['score']:.3f}] {h['code']}: {preview}")
        