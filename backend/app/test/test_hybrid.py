from app.rag.pipeline import retrieve_sops

queries = [
    "Protocol 4B",                                   # the hard case!
    "the respiratory ward is overflowing",
    "we are running out of ventilators",
]

for q in queries:
    print(f"\n=== QUERY: {q} ===")
    results = retrieve_sops(q, top_n=3)
    for r in results:
        preview = r["text"][:60] + "..."
        print(f"  rerank={r['rerank_score']:.3f} | {r['code']}: {preview}")