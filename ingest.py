from PyPDF2 import PdfReader

def load_pdf (path):
  """Load text per page from a PDF file"""
  reader = PdfReader (path)
  pages= []
  for page in reader.pages:
    text=page.extract_text()
    if text: #sjekk at det ikke er NONE
      pages.append(text)
  return pages

def chunk_text (text, chunk_size=200, overlap=30):
  #Split text into smaller chunks
  words=text.split()
  chunks=[]
  start=0
  cid=0

  while start < len(words):
    end=min(start+chunk_size, len(words))
    piece=" ".join(words[start:end]).strip()
    if piece:
      chunks.append({
        "id": cid,
        "text": piece,
        "start_word": start,
        "end_word": end})
      cid +=1
    if end == len(words):
      break
    start = max(end - overlap, start+1)
  
  return chunks

if __name__ == "__main__":
    # Mini-test: last inn PDF, join sider, chunk, og print litt statistikk
    pages = load_pdf("data/test.pdf")   # legg inn din fil
    print("Antall sider:", len(pages))

    full_text = "\n\n".join(pages)
    chunks = chunk_text(full_text, chunk_size=200, overlap=30)
    print("Antall chunks:", len(chunks))
    #sjekk to første chunker
    for c in chunks [:4]:
        print(f"\n# Chunk {c['id']} ({c['start_word']}–{c['end_word']}):\n{c['text'][:300]}...")
