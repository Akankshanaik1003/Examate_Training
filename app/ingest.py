"""ingest.py - clean the raw TNAU page into CaneMitra records (Day 3, S1).

Reads data/raw/tnau_sugarcane.html, writes data/records.json.
Run from the repo root:  python -m app.ingest

The TNAU page has ~35 layout/data tables. We use three of them:
  * "Variety | Duration (Month) | Cane yield (t/ha) | CCS% | CCS(t/ha)"  -> main data
  * "Variety | Performance"                                              -> traits
  * "Early | Mid | Late | Special" (Factory/Jaggery sub-columns)         -> seasons
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

SEASONS = ["early", "mid", "late", "special"]   # column pairs of the season table


# ---------- cleaning helpers ----------

def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def key(name: str) -> str:
    """Normalise a variety name so 'CoC  23' and 'COC 23' match."""
    return re.sub(r"[^A-Za-z0-9]", "", name).upper()


def to_float(text: str):
    m = re.search(r"\d+(?:\.\d+)?", text.replace(",", ""))
    if not m:
        raise ValueError(f"no number in {text!r}")
    return float(m.group(0))


def table_rows(table) -> list[list[str]]:
    return [[clean_text(c.get_text(" ")) for c in tr.find_all(["td", "th"])]
            for tr in table.find_all("tr")]


# ---------- extraction ----------

def find_table(soup, *header_words):
    """First table whose header row contains all the given words."""
    for t in soup.find_all("table"):
        rows = table_rows(t)
        if rows and all(any(w in cell.lower() for cell in rows[0]) for w in header_words):
            return rows
    return None


def season_map(soup) -> dict:
    """variety key -> list of seasons, from the Early/Mid/Late/Special table."""
    mapping = {}
    for t in soup.find_all("table"):
        rows = table_rows(t)
        if rows and [c.lower() for c in rows[0][:4]] == ["early", "mid", "late", "special"]:
            for row in rows[2:]:
                for col, cell in enumerate(row[:8]):
                    # column pairs (factory, jaggery) -> early, mid, late, special
                    if re.match(r"^(CO|CoC|CoG|CoSi|CoV)\s?[A-Za-z]*\s?\d", cell, re.I):
                        season = SEASONS[col // 2]
                        mapping.setdefault(key(cell), [])
                        if season not in mapping[key(cell)]:
                            mapping[key(cell)].append(season)
            break
    return mapping


def traits_map(soup) -> dict:
    rows = find_table(soup, "variety", "performance") or []
    return {key(r[0]): r[1] for r in rows[1:] if len(r) >= 2 and r[0]}


def extract_rows(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    main = find_table(soup, "variety", "yield")
    if not main:
        print("Could not find the 'Variety / Cane yield' table - check the raw HTML.")
        return []
    seasons, traits = season_map(soup), traits_map(soup)
    print(f"main table: {len(main) - 1} rows | season entries: {len(seasons)} | trait entries: {len(traits)}")
    rows = []
    for cells in main[1:]:
        rows.append({
            "name": cells[0] if cells else "",
            "duration": cells[1] if len(cells) > 1 else "",
            "yield": cells[2] if len(cells) > 2 else "",
            "ccs": cells[3] if len(cells) > 3 else "",
            "seasons": seasons.get(key(cells[0]), []) if cells else [],
            "performance": traits.get(key(cells[0]), "") if cells else "",
        })
    return rows


def to_record(raw: dict, n: int) -> Record:
    name = raw["name"].strip()
    if not name:
        raise ValueError("empty variety name")
    cane_yield = to_float(raw["yield"])               # ValueError -> row skipped
    parts = []
    if raw["duration"]:
        parts.append(f"Duration {raw['duration']} months")
    if raw["ccs"]:
        parts.append(f"CCS {raw['ccs']}%")
    if raw["performance"]:
        parts.append(raw["performance"])
    return Record(
        id=f"T{n:02d}",
        variety_name=name,
        release_year=None,                            # not given on this page
        recommended_seasons=raw["seasons"],
        cane_yield_t_ha={"all_seasons": cane_yield},
        key_traits="; ".join(parts),
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


if __name__ == "__main__":
    main()