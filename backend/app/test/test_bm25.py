from app.rag.sparse import fit_bm25, encode_query

fit_bm25()

sparse = encode_query("Protocol 4B")
print("Sparse vector for 'Protocol 4B':")
print(f"  indices: {sparse['indices'][:10]}")
print(f"  values: {[round(v, 3) for v in sparse['values'][:10]]}")