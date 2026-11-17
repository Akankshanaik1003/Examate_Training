"""Day 7: split source documents into chunks that keep source, page and title."""
import json
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader

RAW_DIR = Path("data/raw")
OUT_FILE = Path("data/chunks.json")
CHUNK_WORDS = 150
OVERLAP = 30


def split_words(text, size=CHUNK_WORDS, overlap=OVERLAP):
    words = text.split()
    step = size - overlap
    chunks = []
    for i in range(0, len(words), step):
        piece = words[i:i + size]
        if len(piece) >= 20:
            chunks.append(" ".join(piece))
    return chunks


def read_pdf(path):
    reader = PdfReader(str(path))
    meta_title = reader.metadata.title if reader.metadata else None
    title = meta_title or path.stem
    for number, page in enumerate(reader.pages, start=1):
        yield title, number, page.extract_text() or ""


def read_html(path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else path.stem
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    yield title, 1, soup.get_text(" ", strip=True)


def load_chunks():
    chunks = []
    for path in sorted(RAW_DIR.iterdir()):
        try:
            if path.suffix.lower() == ".pdf":
                pages = read_pdf(path)
            elif path.suffix.lower() in (".html", ".htm"):
                pages = read_html(path)
            else:
                continue
            for title, page, text in pages:
                for n, piece in enumerate(split_words(text)):
                    chunks.append({
                        "id": f"{path.stem}-p{page}-c{n}",
                        "text": piece,
                        "source": path.name,
                        "page": page,
                        "title": title,
                    })
        except Exception as error:
            print(f"Skipped {path.name}: {error}")
    return chunks


if __name__ == "__main__":
    all_chunks = load_chunks()
    OUT_FILE.write_text(json.dumps(all_chunks, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(all_chunks)} chunks to {OUT_FILE}")