# CaneMitra

A small Python project for working with sugarcane variety records from Maharashtra. The records are hand-entered from the MPKV (Mahatma Phule Krishi Vidyapeeth) sugarcane varieties PDF and can be searched and counted from the command line.

**Status:** Day 2 of the build is complete.

## Progress log

### Day 1 - Project setup

### Day 2 - Records, data access and CLI
- Hand-entered **16 sugarcane varieties** into `data/sample_records.json`, each checked against the MPKV PDF.
- **S1:** `day02_s1.py` loads the records, prints them all, searches by keyword and counts records per season and per institute.
- **S2:** moved the logic into a reusable package, `app/records.py` (load, search, count, get by id), with a menu-driven command line in `app/cli.py`.
- Added a virtual environment, `requirements.txt` and `.gitignore`.
- Added the original MPKV PDF to the repo as the source for the data.

## Project structure

```
.
├── README.md
├── .gitignore
├── requirements.txt
├── day02_s1.py              # S1: standalone script
├── app/
│   ├── __init__.py          # empty, marks app as a package
│   ├── records.py           # load_records, search, count_by, get_by_id
│   └── cli.py               # command-line menu
└── data/
    ├── sample_records.json  # 16 variety records
    └── source/
        └── mpkv_sugarcane_varieties.pdf   # original source document
```

## Setup (Windows)

```
python -m venv .venv
.venv\Scripts\activate
```

Day 2 uses only the Python standard library, so there is nothing to install yet. When later days add packages, install them and run `pip freeze > requirements.txt`.

## How to run

Run both commands from the repo root.

**S1 script** - prints all records, then asks for a keyword and shows counts:
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

## Data format

Each record in `data/sample_records.json` has these fields:

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

## Source

Data comes from the MPKV sugarcane varieties document:
https://mpkv.ac.in/Uploads/Research/09%20-%20Sugarcane_20230830095518.pdf

A copy is kept at `data/source/mpkv_sugarcane_varieties.pdf`.

## Git workflow

Each file is committed on its own with a message starting `D2:`. Check `git status` before committing and make sure `.venv` never shows up as staged.

