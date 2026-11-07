"""fetch.py - download source documents into data/raw/ (Day 3, S2).

Run from the repo root:  python -m app.fetch
"""
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# file name to save as -> URL.  Replace the third entry with a real source.
URLS = {
    "tnau_sugarcane.html": "https://agritech.tnau.ac.in/agriculture/sugarcrops_sugarcane.html",
    "mpkv_sugarcane.pdf": "https://mpkv.ac.in/Uploads/Research/09%20-%20Sugarcane_20230830095518.pdf",
    "third_source.html": "https://REPLACE-WITH-A-REAL-SUGARCANE-PAGE",
}

HEADERS = {"User-Agent": "CaneMitra/0.1 (training project)"}


def download(url: str, dest: Path) -> bool:
    """Download one URL to dest. Returns True on success, False on any failure."""
    try:
        r = requests.get(url, timeout=20, headers=HEADERS)
        r.raise_for_status()                       # 4xx/5xx -> exception
    except requests.exceptions.Timeout:
        print(f"TIMEOUT: {url}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"FAILED : {url} -> {e}")
        return False
    dest.write_bytes(r.content)                    # bytes, so PDFs are not corrupted
    print(f"OK     : {dest.name} ({len(r.content)} bytes)")
    return True


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    ok = sum(download(url, RAW / name) for name, url in URLS.items())
    print(f"\n{ok}/{len(URLS)} documents downloaded to {RAW}")


if __name__ == "__main__":
    main()