"""tools.py - Day 9, S1: the tools the CaneMitra agent can call.

Two tools:
    cane_harvest_window(variety, season, planting_date)  -> earliest and latest harvest month
    rag_search(query, top_k)                             -> top chunks from the Chroma index (Day 8)

Every tool returns a plain dict. On bad input a tool returns {"error": "..."}
instead of raising, so the agent can read the error and fix its next call.
"""
import calendar
import re
from datetime import date, datetime
from functools import lru_cache

from app.records import load_all_records

# Month names are written by hand so the output does not depend on the computer's locale.
MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

# TNAU records have no duration field; the text is inside key_traits, e.g. "Duration 10 - 11 months".
DURATION_TEXT = re.compile(r"Duration\s+(\d+)(?:\s*-\s*(\d+))?\s*months", re.IGNORECASE)


@lru_cache(maxsize=1)
def _records() -> tuple:
    return tuple(load_all_records())


def _norm(text: str) -> str:
    """'Co 419', 'co-419' and 'CO419' all become 'co419'."""
    return re.sub(r"[^a-z0-9]", "", str(text).lower())


def add_months(start: date, months: int) -> date:
    """start + months, using only datetime/calendar. 31 Jan + 1 month = 28 (or 29) Feb."""
    year_shift, month_index = divmod(start.month - 1 + months, 12)
    year = start.year + year_shift
    month = month_index + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _month_label(d: date) -> str:
    return f"{MONTH_NAMES[d.month - 1]} {d.year}"


def find_variety(name: str, records=None) -> dict | None:
    """Find a record by variety name, ignoring case, spaces and dashes."""
    wanted = _norm(name)
    for r in (records if records is not None else _records()):
        if _norm(r["variety_name"]) == wanted:
            return r
    return None


def duration_for(record: dict, season: str) -> tuple[int, int] | None:
    """(min_months, max_months) for this record and season, or None if the record does not say."""
    # MPKV records: "duration_months": {"adsali": [16, 18], "suru": [12, 14]}
    per_season = record.get("duration_months") or {}
    if season in per_season:
        low, high = per_season[season]
        return int(low), int(high)
    # TNAU records: the duration is in the text and is the same for every season.
    found = DURATION_TEXT.search(record.get("key_traits", ""))
    if found:
        low = int(found.group(1))
        high = int(found.group(2) or low)
        return low, high
    return None


def cane_harvest_window(variety: str, season: str, planting_date: str, records=None) -> dict:
    """Earliest and latest harvest month for a variety planted on planting_date (YYYY-MM-DD) in a season."""
    season = str(season).strip().lower()

    record = find_variety(variety, records)
    if record is None:
        return {"error": f"No variety named '{variety}' in the records."}

    if season not in record["recommended_seasons"]:
        return {"error": f"{record['variety_name']} is not recommended for '{season}'. "
                         f"Recommended seasons: {', '.join(record['recommended_seasons'])}."}

    try:
        planted = datetime.strptime(str(planting_date).strip(), "%Y-%m-%d").date()
    except ValueError:
        return {"error": f"planting_date '{planting_date}' is not a valid date. Use YYYY-MM-DD, e.g. 2026-12-15."}

    duration = duration_for(record, season)
    if duration is None:
        return {"error": f"The records do not give a duration for {record['variety_name']} in '{season}'."}

    low, high = duration
    earliest = add_months(planted, low)
    latest = add_months(planted, high)
    return {
        "variety": record["variety_name"],
        "record_id": record["id"],
        "season": season,
        "planting_date": planted.isoformat(),
        "duration_months": [low, high],
        "earliest_harvest": _month_label(earliest),
        "latest_harvest": _month_label(latest),
        "source_url": record.get("source_url", ""),
    }


def rag_search(query: str, top_k: int = 3) -> dict:
    """Search the document chunks (Day 8 retrieval). The agent reads the text and writes the answer itself."""
    from app.rag import retrieve  # imported here so tools.py loads fast and cane_harvest_window works without the index

    try:
        top_k = max(1, min(int(top_k), 5))
    except (TypeError, ValueError):
        top_k = 3
    hits = retrieve(str(query), top_k)
    return {
        "query": query,
        "chunks": [
            {"id": h["id"], "source": h["source"], "page": h["page"], "title": h["title"],
             "score": h["score"], "text": h["text"][:600]}
            for h in hits
        ],
    }


# name -> (function, what the model is told about it)
TOOLS = {
    "rag_search": (
        rag_search,
        'rag_search(query: str, top_k: int = 3) - search the sugarcane documents. '
        'Use it for any question about varieties, traits, soil, disease, yield or seasons. '
        'Returns chunks with ids; cite the ids you use.',
    ),
    "cane_harvest_window": (
        cane_harvest_window,
        'cane_harvest_window(variety: str, season: str, planting_date: str) - earliest and latest harvest month. '
        'variety like "Co 419"; season is one of adsali, suru, preseasonal (MPKV) or early, mid, late (TNAU); '
        'planting_date is YYYY-MM-DD.',
    ),
}


def tool_descriptions() -> str:
    return "\n".join(f"- {desc}" for _, desc in TOOLS.values())


def run_tool(name: str, args: dict) -> dict:
    """Run a tool by name. Never raises: unknown tools and bad arguments come back as {"error": ...}."""
    if name not in TOOLS:
        return {"error": f"Unknown tool '{name}'. Available: {', '.join(TOOLS)}."}
    if not isinstance(args, dict):
        return {"error": "args must be a JSON object."}
    try:
        return TOOLS[name][0](**args)
    except TypeError as e:  # wrong or missing argument names
        return {"error": f"Bad arguments for {name}: {e}"}
    except Exception as e:  # e.g. the Chroma index is missing
        return {"error": f"{name} failed: {type(e).__name__}: {e}"}


if __name__ == "__main__":
    print(cane_harvest_window("Co 419", "suru", "2026-12-15"))
    print(cane_harvest_window("Co 419", "adsali", "2026-07-20"))