from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np 
from ingest import load_pdf, chunk_text

def build_tfidf(chunks): #lager term frequency inverse document frequency formel
  texts = [c["text"] for c in chunks] #henter ut tekst fra hver chunk
  ids = [c["id"] for c in chunks] #registrerer id til hver chunk
  vectorizer = TfidfVectorizer() #lager ordforråd og frekvens i en tabell
  X = vectorizer.fit_transform(texts)  #fit for å huske ordene. transform for å lage en tabnell med det
  return vectorizer, X, ids #Bruk tallene X i vectorizer og gi deretter ID

def query_tfidf(vectorizer, X, chunks, query, top_k=5): #bruk tf-idf tallene, gjør spørsmålene til kosine med retning og finn de topp fem chunksene med samme kosine likhet
  q = vectorizer.transform([query]) #verdsett queryen
  sims = linear_kernel(q, X).ravel() #finn kosine likhet med chunks
  top_idx = np.argsort(sims) [::-1] [:top_k] #rangerer de likeste kosinene

  results = [] #her kommer resultatene
  for rank, idx in enumerate(top_idx, 1):  #for løkke for å definere de beste kildene
    results.append({ #rekkefølge
      "rank": rank, #plass
      "chunk_id": chunks[idx] ["id"], #id
      "score": float(sims[idx]), #likhet
      "preview": chunks[idx] ["text"] [:150].replace("\n", " ") #utdrag
    })
  return results 

if __name__ == "__main__": #kun kjør når inne i index_tfidf.py fila
  pages = load_pdf("data/test.pdf") #hent pdf sidene
  text = "\n".join(pages) #lag en stor tekst av pdfene
  chunks = chunk_text(text, chunk_size=200, overlap=30) #lag chunk av teksten på 200 tegn og ta med 30 fra forrige chunk
  print("Antall chunks:", len(chunks))

  vectorizer, X, ids = build_tfidf(chunks) #hent tfidf program til chunksene
  for q in ["økonomi", "medlemmer", "hall", "NM", "dugnad"]: #lager fiktive spørsmål q av enkelte ord
    print(f"\n=== Query: {q} ===") #skriv ut spørsmålene
    hits = query_tfidf(vectorizer, X, chunks, q, top_k=3) #finn de 3 mest relevante chunksene
    for h in hits: #for hver relevante chunk
      print(f"[{h['rank']}] id={h['chunk_id']} score={h['score']:.4f} :: {h['preview']}") #print rangering, id, likhet og et utdrag
