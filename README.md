# CaneMitra

A small Python project for working with sugarcane variety records. The Maharashtra records are hand-entered from the MPKV (Mahatma Phule Krishi Vidyapeeth) sugarcane varieties PDF; a second set is cleaned automatically from the TNAU (Tamil Nadu Agricultural University) crop guide. Records can be searched and counted from the command line.

**Status:** Day 3 of the build is complete.

## Progress log

### Day 1 - Project setup
**Project card**

- **Product:** CaneMitra, a simple sugarcane farming assistant (Mitra = friend) that answers common crop questions.
- **User:** Sugarcane farmers in Maharashtra, and students or advisors who support them.
- **Problem:** Farmers often lack quick, reliable guidance on irrigation, fertilizer timing, pests and harvest readiness, which leads to lower yield and wasted inputs.
- **Data source:** Sugarcane crop guides from agricultural universities and the state agriculture department, plus sugar factory harvest schedules (to be added in later days).

**Files**

- `day01_intro.py`: prints the project card using variables and f-strings, then asks the user's name and question with `input()`.
- `day01_menu.py`: while-loop menu (about CaneMitra, sample questions, harvest-readiness rule check, exit).

### Day 2 - Records, data access and CLI
- Hand-entered **16 sugarcane varieties** into `data/sample_records.json`, each checked against the MPKV PDF.
- **S1:** `day02_s1.py` loads the records, prints them all, searches by keyword and counts records per season and per institute.
- **S2:** moved the logic into a reusable package, `app/records.py` (load, search, count, get by id), with a menu-driven command line in `app/cli.py`.
- Added a virtual environment, `requirements.txt` and `.gitignore`.
- Added the original MPKV PDF to the repo as the source for the data.

### Day 3 - Fetching and ingesting real data
- **S2:** `app/models.py` defines a `Record` dataclass (`id`, `variety_name`, `release_year`, `recommended_seasons`, `cane_yield_t_ha`, `key_traits`, `source_url`).
- **S2:** `app/fetch.py` downloads 3 source documents into `data/raw/` with `requests`, using a 20 second timeout and handling timeouts, HTTP errors and connection errors. A failed download is reported and does not stop the others.
- **S1:** `app/ingest.py` reads the raw TNAU page, picks out the variety, performance and season tables, cleans the values, skips bad rows with `try/except`, and saves `data/records.json` (42 records).
- Added `requests` and `beautifulsoup4` to `requirements.txt`.
- Missing values are stored as `null` or empty, never invented.

## Project structure

```
.
├── README.md
├── .gitignore
├── requirements.txt
├── day01_intro.py           # Day 1: project introduction and user question
├── day01_menu.py            # Day 1: sample questions and season menu
├── day02_s1.py              # Day 2 S1: standalone script
├── app/
│   ├── __init__.py          # empty, marks app as a package
│   ├── models.py            # Day 3: Record dataclass
│   ├── fetch.py             # Day 3: download sources into data/raw/
│   ├── ingest.py            # Day 3: clean raw data into data/records.json
│   ├── records.py           # load_records, search, count_by, get_by_id
│   └── cli.py               # command-line menu
└── data/
    ├── raw/                 # Day 3: downloaded source files
    ├── records.json         # Day 3: cleaned TNAU records (output of ingest)
    ├── sample_records.json  # Day 2: 16 hand-entered MPKV variety records
    └── source/
        └── mpkv_sugarcane_varieties.pdf   # original source document
```

## Setup (Windows)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Day 3 needs `requests` and `beautifulsoup4`. After adding a package, run `pip freeze > requirements.txt`.

## How to run

Run all commands from the repo root.

**Day 1 project introduction:**
```
python day01_intro.py
```

**Day 1 sample-question and season menu:**
```
python day01_menu.py
```

**Day 2 S1 script** - prints all records, then asks for a keyword and shows counts:
```
python day02_s1.py
```

**CLI menu:**
```
python -m app.cli
```

Menu options:

| Choice | Action |
|--------|--------|
| 1 | List all varieties |
| 2 | Search by keyword (name, season or traits) |
| 3 | Count varieties per season |
| 4 | Count varieties per institute |
| 5 | Get one variety by id (for example `V10`) |
| 0 | Exit |

Example keywords to try: `jaggery`, `saline`, `smut`, `drought`, `adsali`.

**Day 3 - download the sources, then clean them:**
```
python -m app.fetch
python -m app.ingest
```

`fetch` prints `OK`, `TIMEOUT` or `FAILED` for each document. `ingest` prints how many records it saved and skipped, and writes `data/records.json`.

## Data format

### `data/sample_records.json` (MPKV, Maharashtra, hand-entered)

| Field | Meaning |
|-------|---------|
| `id` | Record id, `V01` to `V16` |
| `variety_name` | Variety name, with the code in brackets where given |
| `release_year` | Year of release |
| `institute` | Releasing institute (CSRS Padegaon or RSJRS Kolhapur) |
| `recommended_seasons` | Any of `adsali`, `preseasonal`, `suru` |
| `cane_yield_t_ha` | Cane yield in tonnes per hectare, per season |
| `duration_months` | Crop duration as `[min, max]` months, per season |
| `key_traits` | Short description of strengths and weaknesses |
| `state` | State (Maharashtra) |
| `source_url` | Web link to the MPKV PDF |

Data notes:
- **V13 (Phule 09057):** the PDF gives no cane yield, so `cane_yield_t_ha` is empty. The CLI shows "not given in source".
- **V16 (Phule 13007):** the PDF gives one yield for all seasons, stored under the key `all_seasons`.
- **V14 and V15:** the PDF lists a crop duration of 12 months, stored as `[12, 12]`.

### `data/records.json` (TNAU, Tamil Nadu, produced by `app.ingest`)

| Field | Meaning |
|-------|---------|
| `id` | Record id, `T01` to `T42` |
| `variety_name` | Variety name as written on the page |
| `release_year` | Always `null` - the page does not give it |
| `recommended_seasons` | Any of `early`, `mid`, `late`, `special`; empty if the page does not list the variety in its season table |
| `cane_yield_t_ha` | `{"all_seasons": value}` in tonnes per hectare |
| `key_traits` | Duration, CCS % and, where the page gives one, a short performance note |
| `source_url` | Web link to the TNAU page |

Data notes:
- TNAU uses Tamil Nadu seasons (early, mid, late, special), which are not the same as Maharashtra's adsali, preseasonal and suru. The two sets are kept separate and their seasons are not converted.
- Only some TNAU varieties appear in the page's season table, so many records have no season.
- The TNAU records are for Tamil Nadu. They are not Maharashtra recommendations.

## Sources

| Source | Used for | Saved as |
|--------|----------|----------|
| MPKV sugarcane varieties PDF: https://mpkv.ac.in/Uploads/Research/09%20-%20Sugarcane_20230830095518.pdf | 16 hand-entered Maharashtra records | `data/raw/mpkv_sugarcane.pdf`, `data/source/mpkv_sugarcane_varieties.pdf` |
| TNAU Agritech sugarcane page: https://agritech.tnau.ac.in/agriculture/sugarcrops_sugarcane.html | 42 cleaned records | `data/raw/tnau_sugarcane.html` |
| Third source: (add the name and URL you used in `app/fetch.py`) | Extra reference document | `data/raw/` |

### Day 4 - API, analysis and smart search
- **S1:** `app/main.py` is a FastAPI service with `GET /health`, `GET /records?limit=`, `GET /records/{id}` (404 if missing), `GET /search?q=` and `POST /questions`.
- **S2:** `analysis/explore.py` prints 3 facts about the records using pandas. `app/smart_search.py` ranks records with TF-IDF and cosine similarity (scikit-learn) and powers `/search` and `/questions`.
- `app/records.py` gained `load_all_records()`, which combines the MPKV and TNAU records (58 in total).
- Tagged the repo `week-1`.

## How to run the API

pip install -r requirements.txt
uvicorn app.main:app --reload

Open http://127.0.0.1:8000/docs to try every endpoint in the browser.

| Endpoint | What it does |
|----------|--------------|
| `GET /health` | Returns status and record count |
| `GET /records?limit=5` | First 5 records (default 10) |
| `GET /records/V10` | One record, or 404 if the id does not exist |
| `GET /search?q=drought jaggery` | Best matching records with a similarity score |
| `POST /questions` | Body `{"question": "..."}`; returns the closest variety, its traits and source |

python -m analysis.explore