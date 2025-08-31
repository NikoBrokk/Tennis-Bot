# ingest.py
# Formål: lese PDF -> rense tekst -> lage ord-baserte chunks + enkle diagnoser

import re
from typing import List, Dict
from PyPDF2 import PdfReader

# ---------------------------
# 1) RENSING
# ---------------------------
def clean_text(s: str) -> str:
    """
    En enkel 'noise gate' for PDF-tekst:
    - fjerner \r
    - limer sammen ord delt over linjeskift: "repa-\nrasjon" -> "reparasjon"
    - gjør linjeskift til mellomrom
    - komprimerer dobbelte mellomrom
    TODO: vurder å normalisere whitespace foran/etter punktum/komma ved behov
    """
    s = s.replace("\r", "")
    s = re.sub(r"-\n\s*", "", s)     # orddeling ved linjeslutt
    s = re.sub(r"\n+", " ", s)       # linjeskift -> space
    s = re.sub(r"\s{2,}", " ", s)    # dobbel+ space -> enkel
    return s.strip()

# ---------------------------
# 2) PDF -> PAGES
# ---------------------------
def load_pdf(path: str) -> List[str]:
    """
    Leser PDF og returnerer en liste med renset tekst per side.
    NB: Skannede PDF-er uten OCR vil kunne gi tom tekst.
    """
    reader = PdfReader(path)
    pages: List[str] = []
    for i, p in enumerate(reader.pages):
        raw = p.extract_text() or ""
        txt = clean_text(raw)
        # TODO: sett en minstegrense hvis du vil hoppe over "nesten tomme" sider
        pages.append(txt)
    return pages

def page_word_counts(pages: List[str]) -> List[int]:
    """Antall ord per side (nyttig for en rask sanity-check)."""
    counts: List[int] = []
    for p in pages:
        counts.append(len(p.split()) if p and p.strip() else 0)
    return counts

# ---------------------------
# 3) CHUNKING (ORD-BASERT)
# ---------------------------
def chunk_text(text: str, chunk_size: int = 200, overlap: int = 30) -> List[Dict]:
    """
    Del opp i ord-baserte biter med overlapp.
    - chunk_size = antall ORD per chunk (ikke tegn)
    - overlap = antall ORD som gjentas i neste chunk for å bevare kontekst
    Returnerer en liste av dicts med id, text, start_word, end_word.
    """
    # TODO: vurder senking til lower() her hvis du vil gjøre alt case-insensitive tidlig
    words = text.split()
    chunks: List[Dict] = []
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
        # sikre fremdrift og overlapp
        start = max(end - overlap, start + 1)

    return chunks

# ---------------------------
# 4) LITEN DIAGNOSEHJELPER
# ---------------------------
def print_overlap_check(chunks: List[Dict], k: int = 30) -> None:
    """Vis siste k ord i chunk i og første k ord i chunk i+1 (for de to første parene)."""
    for i in range(min(2, len(chunks) - 1)):
        a = chunks[i]["text"].split()
        b = chunks[i + 1]["text"].split()
        print(f"\n[Overlap-sjekk] mellom chunk {i} og {i+1}:")
        print("...A(slutt):", " ".join(a[-k:]))
        print("B(start)...:", " ".join(b[:k]))

# ---------------------------
# 5) QUICK TEST (bare når fila kjøres direkte)
# ---------------------------
if __name__ == "__main__":
    PDF_PATH = "data/test.pdf"

    pages = load_pdf(PDF_PATH)
    print("Antall sider:", len(pages))
    print("Ord per side:", page_word_counts(pages)[:5], "...")

    full_text = "\n\n".join(pages)
    chunks = chunk_text(full_text, chunk_size=200, overlap=30)
    print("Antall chunks:", len(chunks))

    for c in chunks[:2]:
        print(f"\n# Chunk {c['id']} ({c['start_word']}–{c['end_word']}):\n{c['text'][:300]}...")
    print_overlap_check(chunks, k=30)
