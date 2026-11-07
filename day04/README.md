# Day 4 - API, analysis and smart search

**Task (D4, Sat 7 Nov):**
- **S1:** `app/main.py` is a FastAPI service for CaneMitra with `GET /health`, `GET /records?limit=`, `GET /records/{id}` (404 if missing), `GET /search?q=` and `POST /questions`. The README has a "How to run" section.
- **S2:** `analysis/explore.py` prints 3 facts about the CaneMitra records with pandas. `app/smart_search.py` ranks records with TF-IDF and cosine similarity and powers `/search`. Tag `week-1`.

## Where the Day 4 files are
The code is shared with other days, so it lives in `app/` and `analysis/`, not in this folder.

| Task part | File | Path |
|-----------|------|------|
| S1 | FastAPI service with all 5 endpoints | [`app/main.py`](../app/main.py) |
| S2 | TF-IDF + cosine similarity ranking | [`app/smart_search.py`](../app/smart_search.py) |
| S2 | 3 facts with pandas | [`analysis/explore.py`](../analysis/explore.py) |
| S1 | `load_all_records()` combines the MPKV and TNAU records (58) | [`app/records.py`](../app/records.py) |
| Both | Added `fastapi`, `uvicorn`, `pandas`, `scikit-learn` | [`requirements.txt`](../requirements.txt) |

## How to run
Run from the repository root:

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to try every endpoint in the browser.

| Endpoint | What it does |
|----------|--------------|
| `GET /health` | Returns the status and the number of records (58) |
| `GET /records?limit=5` | First 5 records (default 10) |
| `GET /records/V10` | One record, or 404 if the id does not exist |
| `GET /search?q=saline soil` | Best matching records with a similarity score |
| `POST /questions` | Body `{"question": "..."}`; returns the closest variety, its traits and its source |

Analysis script:
```
python -m analysis.explore
```

## The 3 facts from `analysis/explore.py`
1. Top 3 cane yields: COC 779 (204.6 t/ha), Phule 265 (200.0) and COC 777 (171.3).
2. Average Maharashtra yield per season: adsali 165.0, preseasonal 137.3, suru 117.2 t/ha.
3. Varieties whose notes mention drought: 7 in the MPKV records and 7 in the TNAU records.

## How the search works
Each record's name, seasons, traits, institute and state are joined into one text. TF-IDF turns every text and the query into vectors, and cosine similarity ranks the records. Records with a score of 0 are dropped.

## Notes
- TF-IDF matches words, not meaning. Short keyword queries like `saline soil` work well. Long questions can match on filler words.
- `POST /questions` returns the best matching records. It does not generate a written answer.
- The TNAU records are for Tamil Nadu and appear in search next to Maharashtra ones. Every result carries its `source_url`.