from PyPDF2 import PdfReader

def load_pdf (path):
  """Load text per page from a PDF file
  ARGS: 
  path (str): Path to PDF file.
  REturns: 
  list of str: One string per page of text
  """
  reader = PdfReader (path)
  pages= []
  for page in reader.pages:
    text=page.extract_text()
    if text: #sjekk at det ikke er NONE
      pages.append(text)
  return pages

def chunk_text (text, chunk_size=200):
  "Split text into smaller chunks"
  return []

if __name__ == "__main__":
  pages=load_pdf("data/test.pdf) 
  print("Antall sider:", len(pages))
