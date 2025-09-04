from pathlib import Path  # trygg håndtering av filstier
import requests  # bibliotek for HTTP-henting av nettsider

BASE_DIR = Path(__file__).resolve().parents[1]  
# ?.resolve() = gjør til absolutt sti
# .parents[1] = gå opp to nivå (fra scripts/ → til prosjektrot)
# Vi bruker BASE_DIR senere når vi skal lagre i data/

START_URL = "https://www.askertennis.no/"  
# første nettsiden vi tester på (OBS: du hadde "hhtps" og 1 / for lite)

HEADERS = {
    "User-Agent": "AskerTennisRAG/0.1 (+https://github.com/NikoBrokk/Tennis-Bot)"
}  
# Forteller serveren "hvem" vi er (høflig og nyttig hvis nettsiden logger trafikk)

def fetch_html(url: str) -> str:  
    # Funksjon som henter ut rå HTML fra en URL
    resp = requests.get(url, headers=HEADERS, timeout=20)  
    #? requests.get(...) = sender HTTP-forespørsel
    # headers=HEADERS = sender med vår User-Agent
    # timeout=20 = venter maks 20 sek før vi gir opp
    resp.raise_for_status()  
    #? Sjekker HTTP-statuskode: 
    # 200 = OK → går videre
    # 404, 500 osv. → kaster en Exception umiddelbart
    return resp.text  
    #? returnerer selve HTML-teksten som en streng

if __name__ == "__main__":  
    print(f"[TEST] Henter HTML fra: {START_URL}")
    try:
        html = fetch_html(START_URL)  
        # kaller funksjonen vår → henter HTML fra forsiden
        print("[TEST] OK: mottok HTML")
        print(f"[TEST] Antall tegn i HTML: {len(html)}")  
        # teller tegn som enkel sanity check
        print("[TEST] Utdrag (første 300 tegn):")
        print(html[:300].replace("\n", " ") + " ...")  
        # viser starten på HTML-en (uten linjeskift)
    except requests.HTTPError as e:  
        #? Fanges hvis statuskode ≠ 200 (f.eks. 404 Not Found)
        print(f"[TEST] HTTP-feil: {e}")
    except requests.RequestException as e:  
        #? Fanger alle andre requests-relaterte feil (nettverk nede, timeout, osv.)
        print(f"[TEST] Nettverksfeil: {e}")
