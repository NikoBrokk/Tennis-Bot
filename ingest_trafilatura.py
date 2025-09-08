import os 
import pathlib
import trafilatura
from urllib.parse import urlparse

SITEMAP_URL = "https://askertennis.no/sitemap.xml"

OUT_DIR = pathlib.Path("data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

urls = list(trafilatura.sitemaps.sitemap_search(SITEMAP_URL))

for url in urls[:10]:
  downloaded = trafilatura.fetch_url(url)
  if not downloaded:
    continue
  md = trafilatura.extract(downloaded, output="markdown")
  if not md:
    continue


  slug = urlparse(url).path.strip("/").replace("/", "_") or "index"
  filepath = OUT_DIR / f"{slug}.md"

  with open(filepath, "w", encoding="utf-8") as f:
    f.write(md)

  print(f"LAGRET: {filepath}")
