from pathlib import Path  # trygg håndtering av filstier
import time 
import requests  # bibliotek for HTTP-henting av nettsider
from bs4 import BeautifulSoup #hentet HTML fra url
import re

BASE_DIR = Path(__file__).resolve().parents[1]  
OUTPUT_DIR = BASE_DIR / "data"  #legg tekstene i datafila
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

def slugify(url: str) -> str: #fra url til filnavn i data/
    s = url.replace("https://", "").replace("http://", "")
    s = s.rstrip("/")
    s = s.replace("www.askertennis.no", "")
    s = s.replace("/", "_")
    if not s:
        s = "forside"
    return s

def save_text(text: str, url: str) -> Path: #tar string og slugify url til fil med txt
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True) #sjekker om filen eksister, og lager den
    fname = slugify(url) + ".txt"
    path = OUTPUT_DIR / fname
    with path.open("w", encoding="utf-8") as f:
        f.write(f"URL: {url}\n") #skrape URL
        f.write(f"SCRAPED_AT: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n") #skrapetidspunkt
        f.write(text)
    return path

def filter_noise(text: str) -> str:
    # STOP_SUBSTRINGS = uttrykk som ofte er UI/handel-støy og sjelden nyttig faglig
    STOP_SUBSTRINGS = [
        "Handlekurven din", "Fortsett å handle", "Kasse", "Logg på", "Søk",
        "Gå videre til innholdet", "Laster inn", "KJØP NÅ", "BOOK EN BANE", "BOOK HER",
        "Vis alle", "Se mer", "Bli sponsor", "Bli sponsor av", "Sponsorer",
        "Betalingsmåter", "Ved å gjøre et valg vil hele siden lastes inn på nytt.",
        "Facebook", "Instagram", "Norsk (bokmål)", "English", "©",
        "American Express", "Apple Pay", "Google Pay", "Klarna", "Maestro",
        "Mastercard", "Shop Pay", "Union Pay", "Visa",
        "Asker Tennis Gavekort",        # produkt/butikk-spesifikk
        "Vanlig pris", "Salgspris", "Enhetspris",  # nettbutikk-prislinjer
        "Privattime med",               # produktkort-listing gjør lite for kunnskapsbase
    ]
    # PATTERNS = regex som fanger generisk støy (sideindikatorer, prosenter, priser, tomme linjer)
    PATTERNS = [
        r"^\d+\s*/\s*av\s*\d+\s*$",             # "1 / av 5"
        r"\b\d{1,3}%\b",                         # prosentsatser som "50%"
        r"\b\d{1,3}(?:\.\d{3})*,\d{2}\s*kr\b",   # priser "1.349,00 kr" eller "475,00 kr"
        r"^\s*$",                                # tom linje (rydder vi senere uansett)
    ]

    # compile regex én gang for ytelse
    compiled = [re.compile(p, flags=re.IGNORECASE) for p in PATTERNS]  # kompiler alle mønstre
    kept = []                                   # linjer vi beholder
    prev = None                                 # for å unngå direkte duplikater på rad

    for ln in text.splitlines():                # gå gjennom hver linje
        ln_stripped = ln.strip()                # fjern whitespace i begge ender
        ln_lower = ln_stripped.lower()          # lag en "lower" variant for robust søk

        # dropp hvis linjen inneholder noen "stop"-fraser (case-insensitive via lower())
        if any(stop.lower() in ln_lower for stop in STOP_SUBSTRINGS):
            continue

        # dropp hvis linjen matcher noen av regex-mønstrene
        if any(rx.search(ln_stripped) for rx in compiled):
            continue

        # dropp eksplisitte call-to-actions
        if ln_stripped in {"Meld deg på", "Bli med i dag", "Bestill i dag!", "KJØP NÅ"}:
            continue

        # dropp hvis linjen er nøyaktig lik forrige (rett-etter-duplikat)
        if prev is not None and ln_stripped == prev.strip():
            continue

        kept.append(ln_stripped)                # behold linjen
        prev = ln                                # husk for duplikatsjekk

    cleaned = "\n".join(kept)                   # sett sammen beholdte linjer
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)  # maks to\n på rad
    return cleaned                              # gi tilbake filtrert tekst


if __name__ == "__main__":  
    print(f"[TEST] Henter HTML fra: {START_URL}")
    try:
        html = fetch_html(START_URL)  
        # kaller funksjonen vår → henter HTML fra forsiden
        print("[TEST] OK: mottok HTML")
        print(f"[TEST] Antall tegn i HTML: {len(html)}")  

        clean = html_to_text(html)
        print(f"[TEST] Antall tegn i ren tekst: {len(clean)}")
        print("[TEST] Første 10 linjer av ren tekst:")
        for i, ln in enumerate(clean.splitlines()[:10], start=1):
            print(f"{i:02d}: {ln[:120]}")

        filtered = filter_noise(clean)
        print(f" [TEST] Linjer etter filter: {len(filtered.splitlines())}")
        print(f"[TEST] Første 15 linjer etter filter:")
        for i, ln in enumerate(filtered.splitlines() [:15], start=1):
            print(f"{i:02d}: {ln[:120]}")
        
        saved_path = save_text(filtered, START_URL)
        print(f"[TEST] Lagret fil: {saved_path}") 
        print(f"[TEST] Filstørrelse (i bytes): {saved_path.stat().st_size}")
       
    except requests.HTTPError as e:  
        #? Fanges hvis statuskode ≠ 200 (f.eks. 404 Not Found)
        print(f"[TEST] HTTP-feil: {e}")
    except requests.RequestException as e:  
        #? Fanger alle andre requests-relaterte feil (nettverk nede, timeout, osv.)
        print(f"[TEST] Nettverksfeil: {e}")
