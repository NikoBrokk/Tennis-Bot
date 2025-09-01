import os  # API nøkkel
from ingest import load_pdf, chunk_text  # ingest-funksjoner, fra PDF til chunks
from index_vec import embed_chunks, build_nn_index, query_nn  # embeddings + NN
from openai import OpenAI

def rag_answer(query, pdf_path="data/test.pdf", k=3):  
    # 1) Last og chunk PDF
    pages = load_pdf(pdf_path)
    text = "\n".join(pages)
    chunks = chunk_text(text, chunk_size=200, overlap=30)

    # 2) Bygg embeddings + index
    embs, ids, model = embed_chunks(chunks)
    nn = build_nn_index(embs)

    # 3) Retrieval
    hits = query_nn(nn, chunks, query, model, top_k=k)
    context = "\n\n".join([h["preview"] for h in hits])

    # 4) Prompt til LLM
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""Du er en hjelpsom assistent for Asker Tennis. 
    Skriv et svar på 2-3 setninger. 
    Hvis du ikke finner svaret blant kildene dine, svar "jeg vet ikke".
    Bruk KUN denne informasjonen til å svare: 
    {context}

    Spørsmål: {query}"""
    
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content

if __name__ == "__main__":  
    q = input("Skriv et spørsmål: ")  
    svar = rag_answer(q)  
    print("\n=== SVAR ===\n", svar)  

