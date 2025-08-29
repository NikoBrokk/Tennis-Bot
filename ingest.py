from PyPDF2 import PdfReader

def load_pdf(path):
    """Load text per page from a PDF file"""
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:  # sjekk at det ikke er None/tomt
            pages.append(text)
    return pages

def page_word_counts(pages):
    counts = []
    for p in pages:
        if p and p.strip():
            counts.append(len(p.split()))
        else:
            counts.append(0)  # <- var 'count.append(0)' før (feil navn)
    return counts

def chunk_text(text, chunk_size=200, overlap=30):
    # Split text into smaller chunks
    words = text.split()
    chunks = []
    start = 0
    cid = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        piece = " ".join(words[start:end]).strip()
        if piece:
            chunks.append({
                "id": cid,
                "text": piece,
                "start_word": start,
                "end_word": end  # eksklusiv
            })
            cid += 1
        if end == len(words):
            break
        start = max(end - overlap, start + 1)

    return chunks

def print_overlap_check(chunks, k=30):
    # print siste k ord i chunk i og første k ord i chunk i+1
    for i in range(min(2, len(chunks) - 1)):  # bare to første par
        a = chunks[i]["text"].split()
        b = chunks[i + 1]["text"].split()
        print(f"\n[Overlap-sjekk] mellom chunk {i} og {i+1}:")
        print("...A(slutt):", " ".join(a[-k:]))
        print("B(start)...:", " ".join(b[:k]))

if __name__ == "__main__":
    pages = load_pdf("data/test.pdf")
    print("Antall sider:", len(pages))

    full_text = "\n\n".join(pages)
    chunks = chunk_text(full_text, chunk_size=200, overlap=30)
    print("Antall chunks:", len(chunks))

    for c in chunks[:2]:
        print(f"\n# Chunk {c['id']} ({c['start_word']}–{c['end_word']}):\n{c['text'][:300]}...")
    print_overlap_check(chunks, k=10)
