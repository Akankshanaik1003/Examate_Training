#S1
"""records.py - data access functions for CaneMitra variety records."""
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_records.json"


def load_records(path=DATA_PATH):
    """Load all variety records from the JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def search(records, keyword):
    """Return records whose name, seasons or key_traits contain the keyword (case-insensitive)."""
    kw = keyword.strip().lower()
    results = []
    for r in records:
        text = " ".join([r["variety_name"], " ".join(r["recommended_seasons"]), r["key_traits"]]).lower()
        if kw in text:
            results.append(r)
    return results


def count_by(records, field):
    """Count records per value of a field. List fields (like recommended_seasons) count each item."""
    counts = {}
    for r in records:
        value = r[field]
        values = value if isinstance(value, list) else [value]
        for v in values:
            counts[v] = counts.get(v, 0) + 1
    return counts


def get_by_id(records, record_id):
    """Return the record with this id (e.g. 'V10'), or None."""
    for r in records:
        if r["id"].lower() == record_id.strip().lower():
            return r
    return None

RECORDS_PATH = Path(__file__).resolve().parent.parent / "data" / "records.json"


def load_all_records():
    """Hand-entered MPKV records (V01-V16) plus the cleaned TNAU records (T01-T42), if present."""
    records = load_records()
    if RECORDS_PATH.exists():
        records += load_records(RECORDS_PATH)
    return records