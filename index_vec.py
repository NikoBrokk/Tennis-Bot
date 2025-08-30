from sentence_transformers import SentenceTransformer
import numpy as np 

# tar en chunk og lager en embedding av den
def embed_chunks(chunks, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    # henter ordrett fra chunks
    texts = [c["text"] for c in chunks] 
    model = SentenceTransformer(model_name)
    # lag embedding for alle chunks. 32 tekster av gangen. 
    embs = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    # Bruk float32, numpy, for FAISS
    embs = np.asarray(embs, dtype=np.float32) 
    ids = [c["id"] for c in chunks]
    # gi tallrekken og respektiv id
    return embs, ids

# kjør kun hvis det er index_vec.py som kjører
if __name__ == "__main__":
    # henter ut en test fra ingest.py
    from ingest import load_pdf, chunk_text 
    pages = load_pdf("data/test.pdf")
    full_text = "\n\n".join(pages)
    chunks = chunk_text(full_text, chunk_size=200, overlap=30)
    embs, ids = embed_chunks(chunks)
    print("Antall chunks:", len(chunks))
    print("Embeddings shape:", embs.shape)  # N nummer, D dimensjon
    print("Første 5 ids:", ids[:5])
