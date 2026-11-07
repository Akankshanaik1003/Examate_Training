# Day 3 - Fetching and ingesting real data

**Task (D3, Fri 6 Nov):**
- **S1:** download a first real slice of the CaneMitra data from the TNAU page and the MPKV PDF into `data/raw/`; `app/ingest.py` cleans it into the record fields (`variety_name`, `release_year`, `recommended_seasons`, `cane_yield_t_ha`, `key_traits`, `source_url`) with try/except for bad rows and saves `data/records.json`.
- **S2:** a `Record` dataclass in `app/models.py`; `app/fetch.py` downloads 3+ documents with `requests` (timeouts, error handling).

## Where the Day 3 files are
The code is shared with later days, so it lives in `app/` and `data/`, not in this folder.

| Task part | File | Path |
|-----------|------|------|
| S2 | `Record` dataclass | [`app/models.py`](../app/models.py) |
| S2 | Downloads 3+ documents with timeouts and error handling | [`app/fetch.py`](../app/fetch.py) |
| S1 | Cleans raw data into records, skips bad rows with try/except | [`app/ingest.py`](../app/ingest.py) |
| S1 | Raw downloaded files | [`data/raw/`](../data/raw) |
| S1 | Cleaned output (42 records) | [`data/records.json`](../data/records.json) |
| Both | Added `requests` and `beautifulsoup4` | [`requirements.txt`](../requirements.txt) |

## Sources
| Source | Saved as |
|--------|----------|
| TNAU Agritech sugarcane page: https://agritech.tnau.ac.in/agriculture/sugarcrops_sugarcane.html | `data/raw/tnau_sugarcane.html` |
| MPKV sugarcane varieties PDF: https://mpkv.ac.in/Uploads/Research/09%20-%20Sugarcane_20230830095518.pdf | `data/raw/mpkv_sugarcane.pdf` |
| Third source: WRITE THE NAME AND URL YOU USED IN `app/fetch.py` | `data/raw/` |

## How to run
Run from the repository root:

```
pip install -r requirements.txt
python -m app.fetch
python -m app.ingest
```

`fetch` prints `OK`, `TIMEOUT` or `FAILED` for each document. `ingest` prints `saved 42 records, skipped 0`.

## How ingest works
The TNAU page has about 35 tables, and ingest uses three of them:
1. `Variety | Duration | Cane yield | CCS%` gives the name, yield and duration.
2. `Variety | Performance` gives a short trait note where the page has one.
3. `Early | Mid | Late | Special` gives the seasons.

Varieties are matched across tables by a normalised name (spaces and punctuation removed, upper case). A row whose yield cannot be read raises `ValueError` and is skipped and reported.

## Data notes
- `release_year` is always `null`, because the TNAU page does not give it. No value was invented.
- TNAU seasons (early, mid, late, special) are Tamil Nadu seasons, not Maharashtra's adsali, preseasonal and suru. They are kept separate and not converted.
- Only some varieties appear in the page's season table, so many records have no season.
- These records are for Tamil Nadu and are not Maharashtra recommendations.