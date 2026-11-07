# CaneMitra

CaneMitra (Mitra = friend) is a sugarcane question-answering project for farmers, students and advisors. It collects sugarcane variety records from agricultural university guides, cleans them into one format, and serves them through a command line and a small web API with keyword and TF-IDF search.

**Status:** Week 1 (Days 1-4) is complete. Tag: `week-1`.

## Day-wise progress

Each day has its own folder with a README that explains the task and lists the exact path of every file. Code used by several days lives in the shared `app/`, `analysis/` and `data/` folders.

| Day | Folder | What was built |
|-----|--------|----------------|
| Day 1 | [`day01/`](day01/README.md) | Project card, intro script and interactive menu |
| Day 2 | [`day02/`](day02/README.md) | 16 hand-entered MPKV records, search/count script, reusable data functions and CLI |
| Day 3 | [`day03/`](day03/README.md) | `Record` dataclass, downloader with error handling, ingest of the TNAU page into `data/records.json` |
| Day 4 | [`day04/`](day04/README.md) | FastAPI service, pandas analysis, TF-IDF smart search |

### Day 1 - Project idea and interactive menu
- Defined the project card: product, user, problem and data source.
- `day01/day01_intro.py` prints the card with f-strings and asks the user's name and question.
- `day01/day01_menu.py` is a while-loop menu with sample questions and a planting-month season check.

### Day 2 - Records, data access and CLI
- Hand-entered **16 varieties** from the MPKV sugarcane PDF into `data/sample_records.json`, each checked against the source.
- `day02/day02_s1.py` prints, searches and counts the records.
- `app/records.py` (load, search, count, get by id) and `app/cli.py` (menu CLI).
- Added a virtual environment, `requirements.txt` and `.gitignore`.

### Day 3 - Fetching and ingesting real data
- `app/models.py`: `Record` dataclass.
- `app/fetch.py`: downloads 3 documents into `data/raw/` with `requests`, a 20 second timeout and error handling.
- `app/ingest.py`: cleans the TNAU page into **42 records** in `data/records.json`, skipping bad rows with `try/except`.

### Day 4 - API, analysis and smart search
- `app/main.py`: FastAPI service with `/health`, `/records`, `/records/{id}`, `/search` and `/questions`.
- `app/smart_search.py`: TF-IDF + cosine similarity ranking that powers `/search`.
- `analysis/explore.py`: 3 facts about the records with pandas.
- `app/records.py` gained `load_all_records()`, which combines both data files (58 records).

## Project structure

```
.
├── README.md
├── .gitignore
├── requirements.txt
├── day01/
│   ├── README.md
│   ├── day01_intro.py       # project card and user question
│   └── day01_menu.py        # sample questions and season menu
├── day02/
│   ├── README.md
│   └── day02_s1.py          # print, search and count script
├── day03/
│   └── README.md            # points to app/models.py, fetch.py, ingest.py
├── day04/
│   └── README.md            # points to app/main.py, smart_search.py, analysis/explore.py
├── app/                     # shared package (Days 2-4)
│   ├── __init__.py
│   ├── records.py           # load_records, load_all_records, search, count_by, get_by_id
│   ├── cli.py               # command-line menu
│   ├── models.py            # Record dataclass
│   ├── fetch.py             # download sources into data/raw/
│   ├── ingest.py            # clean raw data into data/records.json
│   ├── smart_search.py      # TF-IDF + cosine similarity search
│   └── main.py              # FastAPI service
├── analysis/
│   ├── __init__.py
│   └── explore.py           # 3 facts with pandas
└── data/
    ├── sample_records.json  # 16 hand-entered MPKV records
    ├── records.json         # 42 cleaned TNAU records (output of ingest)
    ├── raw/                 # downloaded source files
    └── source/
        └── mpkv_sugarcane_varieties.pdf
```

## Setup (Windows)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run every command from the repository root.

## How to run

**Day 1**
```
python day01\day01_intro.py
python day01\day01_menu.py
```

**Day 2**
```
python day02\day02_s1.py
python -m app.cli
```

CLI menu: `1` list all, `2` search by keyword, `3` count per season, `4` count per institute, `5` get by id (for example `V10`), `0` exit.

**Day 3** - download the sources, then clean them:
```
python -m app.fetch
python -m app.ingest
```

**Day 4** - start the API:
```
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs to try every endpoint in the browser.

| Endpoint | What it does |
|----------|--------------|
| `GET /health` | Status and number of records (58) |
| `GET /records?limit=5` | First 5 records (default 10) |
| `GET /records/V10` | One record, or 404 if the id does not exist |
| `GET /search?q=saline soil` | Best matching records with a similarity score |
| `POST /questions` | Body `{"question": "..."}`; returns the closest variety, its traits and source |

Example:
```
curl -X POST http://127.0.0.1:8000/questions -H "Content-Type: application/json" -d "{\"question\": \"saline soil\"}"
```

Run the analysis:
```
python -m analysis.explore
```
It prints the top 3 cane yields, the average Maharashtra yield per season, and how many varieties mention drought tolerance.

## Data

| File | Records | Source | Seasons |
|------|---------|--------|---------|
| `data/sample_records.json` | 16 (`V01`-`V16`) | MPKV PDF, hand-entered | adsali, preseasonal, suru |
| `data/records.json` | 42 (`T01`-`T42`) | TNAU page, cleaned by `app/ingest.py` | early, mid, late, special (where listed) |

Fields of `sample_records.json`: `id`, `variety_name`, `release_year`, `institute`, `recommended_seasons`, `cane_yield_t_ha` (per season), `duration_months` (per season), `key_traits`, `state`, `source_url`.

Fields of `records.json`: `id`, `variety_name`, `release_year` (always `null`), `recommended_seasons`, `cane_yield_t_ha` (`{"all_seasons": value}`), `key_traits` (duration, CCS %, and a short note where the page has one), `source_url`.

Data notes:
- **V13 (Phule 09057):** the PDF gives no cane yield, so `cane_yield_t_ha` is empty.
- **V16 (Phule 13007):** one yield for all seasons, stored under `all_seasons`.
- **V14 and V15:** the PDF lists a duration of 12 months, stored as `[12, 12]`.
- **TNAU records:** the page gives no release year, so it is `null`; no value was invented. TNAU seasons are Tamil Nadu seasons and are not converted to Maharashtra's. Only some varieties appear in the page's season table, so many records have no season.
- The TNAU records are for Tamil Nadu and are not Maharashtra recommendations. Every record keeps its `source_url`.

## Sources

| Source | Used for | Saved as |
|--------|----------|----------|
| MPKV sugarcane varieties PDF: https://mpkv.ac.in/Uploads/Research/09%20-%20Sugarcane_20230830095518.pdf | 16 hand-entered Maharashtra records | `data/raw/mpkv_sugarcane.pdf`, `data/source/mpkv_sugarcane_varieties.pdf` |
| TNAU Agritech sugarcane page: https://agritech.tnau.ac.in/agriculture/sugarcrops_sugarcane.html | 42 cleaned records | `data/raw/tnau_sugarcane.html` |
| Third source: WRITE THE NAME AND URL YOU USED IN `app/fetch.py` | Extra reference document | `data/raw/` |

## Limitations
- Search uses TF-IDF, which matches words and not meaning. Short keyword queries such as `saline soil` work best.
- `POST /questions` returns the best matching records. It does not generate a written answer.
- Season rules and recommendations have not yet been verified against the full source guides and should not be presented as farmer guidance.

## Git workflow

Each file is committed on its own with a message starting with the day, for example `D3:` or `D4:`. Check `git status` before committing and make sure `.venv` never shows up as staged. The `week-1` tag marks the end of Days 1-4.

## Next steps
- Estimate a harvest window from the planting date, season and variety duration.
- Add tests for the record-loading, search and counting functions.
- Verify season rules and recommendations against the source guides.