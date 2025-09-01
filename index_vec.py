from sentence_transformers import SentenceTransformer            # # modell som lager embeddings (vektorer)
import numpy as np                                               # # numeriske matriser
from sklearn.neighbors import NearestNeighbors                   # # nærmeste-nabo-søk (cosine)

def build_nn_index(embs, metric: str = "cosine"):
    nn = NearestNeighbors(n_neighbors=5, metric=metric)          # # forhåndssetter 5, men kan overstyres ved spørretid
    nn.fit(embs)                                                 # # «lær» hvor alle chunk-vektorene ligger (bygg søkestruktur)
    return nn

def query_nn(nn, chunks, query: str, model, top_k: int = 5):
    q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)  # # gjør query til en vektor
    distances, indices = nn.kneighbors(q_emb, n_neighbors=top_k)                    # # finn topp-k nærmeste chunks

    results = []                                                                     # # pakk ut i lesbart format
    for rank, (dist, idx) in enumerate(zip(distances[0], indices[0]), 1):
        results.append({
            "rank": rank,                                                            # # plassering
            "chunk_id": chunks[idx]["id"],                                           # # chunk-ID
            "distance": float(dist),                                                 # # lavere = nærmere (med cosine distance)
            "preview": chunks[idx]["text"][:150].replace("\n", " ")                  # # kort utdrag
        })
    return results

def embed_chunks(chunks, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    texts = [c["text"] for c in chunks]                                             # # hent rå tekst fra hver chunk
    model = SentenceTransformer(model_name)                                         # # last modellen (kan løftes ut og gjenbrukes)
    embs = model.encode(                                                            # # lag vektor for hver chunk
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True                                                   # # normaliser => cosine-distance ~ dot product
    )
    embs = np.asarray(embs, dtype=np.float32)                                       # # float32 er standard for ANN-bibliotek (og sparer minne)
    ids = [c["id"] for c in chunks]                                                 # # behold ID-er for referanse
    return embs, ids, model                                                         # # returner også model så vi kan gjenbruke den

if __name__ == "__main__":
    from ingest import load_pdf, chunk_text                                         # # gjenbruk ingest
    pages = load_pdf("data/test.pdf")                                               # # les PDF
    full_text = "\n\n".join(pages)                                                  # # slå sammen sider
    chunks = chunk_text(full_text, chunk_size=200, overlap=30)                      # # lag ord-baserte chunks

    embs, ids, model = embed_chunks(chunks)                                         # # hent embeddings + model
    nn = build_nn_index(embs, metric="cosine")                                      # # bygg NN-indeks

    print("Antall chunks:", len(chunks))
    print("Embeddings shape:", embs.shape)                                          # # (N, D)
    print("Første 5 ids:", ids[:5])

    for q in ["økonomi", "medlemmer", "hall", "NM", "dugnad"]:                      # # små testspørringer
        print(f"\n=== Query: {q} ===")
        hits = query_nn(nn, chunks, q, model, top_k=3)                              # # finn topp-3 nærmeste
        for h in hits:
            print(f"[{h['rank']}] id={h['chunk_id']} dist={h['distance']:.4f} :: {h['preview']}")
