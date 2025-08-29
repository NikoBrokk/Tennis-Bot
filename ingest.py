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
