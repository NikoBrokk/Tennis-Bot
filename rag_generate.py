import os                      # for å lese OPENAI_API_KEY fra miljø
import time                    # for å måle svartid (latency)
from typing import Dict, Any, List  # tydelige returtyper

from ingest import load_pdf, chunk_text  # PDF -> tekst -> chunks
from index_vec import embed_chunks, build_nn_index, query_nn  # embeddings + NN
from openai import OpenAI        # LLM-klient

# Adapter som UI (Streamlit) kaller
def answer_question(question: str, pdf_path: str = "data/test.pdf", top_k: int = 3) -> Dict[str, Any]:
    t0 = time.time()  # <-- var 'time-time()' før; riktig er time.time()

    # 1) Ingest: last PDF og chunk opp teksten
    pages = load_pdf(pdf_path)            # liste av sider som tekst
    text = "\n".join(pages)               # én stor streng
    chunks = chunk_text(text, chunk_size=200, overlap=30)  # små biter med overlapp

    # 2) Index: lag embeddings og bygg nearest-neighbor-indeks
    embs, ids, model = embed_chunks(chunks)
    nn = build_nn_index(embs)

    # 3) Retrieve: finn de mest relevante chunkene til spørsmålet
    hits = query_nn(nn, chunks, question, model, top_k=top_k)  # <-- bruk riktig param-navn
    context = "\n\n".join([h.get("preview", "") for h in hits])  # <-- manglet sluttparantes før

    # 4) Generate: prompt LLM med konteksten
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = (
        "Du er en hjelpsom assistent for Asker Tennis. "
        "Svar kort (2-3 setninger). Hvis kildene ikke dekker spørsmålet, si 'det står ikke i kildene mine'.\n\n"
        f"KILDER:\n{context}\n\n"     # <-- 'KILDER_' og 'contect' var skrivefeil
        f"SPØRSMÅL: {question}"
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    answer_text = resp.choices[0].message.content  # hent selve svaret

    # 5) Normaliser kilder til et stabilt format for UI
    sources: List[Dict[str, Any]] = []
    for h in hits:
        sources.append({
            "source": h.get("source", "(ukjent)"),
            "page": h.get("page"),
            "score": float(h.get("score", 0.0)),
            "snippet": h.get("preview", "")[:240],  # <-- hadde feil sitat/komma tidligere
        })

    latency_ms = int((time.time() - t0) * 1000)  # ms for UI
    return {"answer": answer_text, "sources": sources, "latency_ms": latency_ms}

# CLI-støtte (frivillig): tekst inn -> tekst ut
def rag_answer(query: str, pdf_path: str = "data/test.pdf", k: int = 3) -> str:
    result = answer_question(query, pdf_path=pdf_path, top_k=k)
    return result["answer"]

if __name__ == "__main__":
    q = input("Skriv et spørsmål: ")
    print("\n=== SVAR ===\n", rag_answer(q))
