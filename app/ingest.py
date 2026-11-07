"""ingest.py - clean the raw TNAU page into CaneMitra records (Day 3, S1).

Reads data/raw/tnau_sugarcane.html, writes data/records.json.
Run from the repo root:  python -m app.ingest
"""
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

from app.models import Record

ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "raw" / "tnau_sugarcane.html"
OUT_FILE = ROOT / "data" / "records.json"
SOURCE_URL = "https://agritech.tnau.ac.in/agriculture/sugarcrops_sugarcane.html"

# field it maps to -> header keywords that identify its column
HEADER_KEYS = [
    ("name", ("variety", "name")),
    ("year", ("year", "release")),
    ("season", ("season",)),
    ("yield", ("yield",)),
    ("traits", ("characteristic", "trait", "feature", "remark", "special", "reaction")),
]

SEASON_WORDS = {
    "adsali": "adsali",
    "pre-seasonal": "preseasonal", "pre seasonal": "preseasonal", "preseasonal": "preseasonal",
    "suru": "suru",
    "early": "early", "mid": "mid", "late": "late",   # Tamil Nadu style seasons
}


# ---------- cleaning helpers ----------

def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse_year(text: str):
    m = re.search(r"\b(19|20)\d{2}\b", text)
    return int(m.group(0)) if m else None


def parse_seasons(text: str) -> list[str]:
    t = text.lower()
    found = []
    for word, norm in SEASON_WORDS.items():
        if word in t and norm not in found:
            found.append(norm)
    return found


def parse_yield(text: str) -> dict:
    nums = re.findall(r"\d+(?:[.,]\d+)?", text)
    if not nums:
        return {}
    return {"all_seasons": float(nums[0].replace(",", ""))}


# ---------- extraction ----------

def map_columns(header_cells: list[str]) -> dict:
    """Work out which column index holds which field, from the header text."""
    mapping = {}
    for i, h in enumerate(header_cells):
        h = h.lower()
        for field_name, keys in HEADER_KEYS:
            if field_name not in mapping and any(k in h for k in keys):
                mapping[field_name] = i
                break
    return mapping


def extract_rows(html: str) -> list[dict]:
    """Return one dict per table row: {'name':..., 'year':..., ...} (raw strings)."""
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    print(f"found {len(tables)} table(s) in the page")
    rows = []
    for t_idx, table in enumerate(tables, 1):
        trs = table.find_all("tr")
        if len(trs) < 2:
            continue
        header = [clean_text(c.get_text(" ")) for c in trs[0].find_all(["th", "td"])]
        mapping = map_columns(header)
        if "name" not in mapping:
            print(f"  table {t_idx}: no variety column in header {header} -> ignored")
            continue
        print(f"  table {t_idx}: using columns {mapping}")
        for tr in trs[1:]:
            cells = [clean_text(c.get_text(" ")) for c in tr.find_all(["td", "th"])]
            row = {f: cells[i] for f, i in mapping.items() if i < len(cells)}
            rows.append(row)
    return rows


def to_record(raw: dict, n: int) -> Record:
    name = raw.get("name", "").strip()
    if not name:
        raise ValueError("empty variety name")
    return Record(
        id=f"T{n:02d}",
        variety_name=name,
        release_year=parse_year(raw.get("year", "")),
        recommended_seasons=parse_seasons(raw.get("season", "")),
        cane_yield_t_ha=parse_yield(raw.get("yield", "")),
        key_traits=raw.get("traits", ""),
        source_url=SOURCE_URL,
    )


def main():
    if not RAW_FILE.exists():
        print(f"{RAW_FILE} not found - run  python -m app.fetch  first.")
        return
    html = RAW_FILE.read_text(encoding="utf-8", errors="ignore")

    good, bad = [], 0
    for n, raw in enumerate(extract_rows(html), 1):
        try:
            good.append(to_record(raw, n).to_dict())
        except (ValueError, KeyError, TypeError, IndexError) as e:
            bad += 1
            print(f"skip row {n}: {e}")

    OUT_FILE.write_text(json.dumps(good, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nsaved {len(good)} records, skipped {bad} -> {OUT_FILE}")
    if not good:
        print("No records. Open data/raw/tnau_sugarcane.html and check how the varieties are laid out.")


if __name__ == "__main__":
    main()