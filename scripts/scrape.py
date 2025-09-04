from pathlib import Path  # trygg håndtering av filstier
import requests  # bibliotek for HTTP-henting av nettsider
from bs4 import BeautifulSoup #fra HTML til string

BASE_DIR = Path(__file__).resolve().parents[1]  
START_URL = "https://www.askertennis.no/"  
HEADERS = {
    "User-Agent": "AskerTennisRAG/0.1 (+https://github.com/NikoBrokk/Tennis-Bot)"
}  

def fetch_html(url: str) -> str:   #fra HTML til string
    resp = requests.get(url, headers=HEADERS, timeout=20)  #henter siden og jobber maks 20 sekunder
    resp.raise_for_status()  #gi feilkode ved 404 eller 500
    return resp.text  

def html_to_text(html: str) -> str: #gjør HTML teksten lesbar for programmet
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]): #fjern unødvendig støy fra HTML
        tag.decompose() #fjern det
    raw = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in raw.splitlines()]
    non_empty = [ln for ln in lines if ln]
    text = "\n".join(non_empty)
    return text

    
if __name__ == "__main__":  
    print(f"[TEST] Henter HTML fra: {START_URL}")
    try:
        html = fetch_html(START_URL)  
        # kaller funksjonen vår → henter HTML fra forsiden
        print("[TEST] OK: mottok HTML")
        print(f"[TEST] Antall tegn i HTML: {len(html)}")  

        clean = html_to_text(html)
        print(f"[TEST] Antall tegn i ren tekst: {len(clean)}")
        print("[TEST] Første 30 linjer av ren tekst:")
        preview_lines = clean.splitlines()[:30]
        for i, ln in enumerate(preview_lines, start=1):
            print(f"{i:02d}: {ln[:120]}")
            
    except requests.HTTPError as e:  
        #? Fanges hvis statuskode ≠ 200 (f.eks. 404 Not Found)
        print(f"[TEST] HTTP-feil: {e}")
    except requests.RequestException as e:  
        #? Fanger alle andre requests-relaterte feil (nettverk nede, timeout, osv.)
        print(f"[TEST] Nettverksfeil: {e}")
