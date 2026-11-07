# Day 2 - Records, data access and CLI

**Task (D2, Thu 5 Nov):** hand-enter 15-20 verified variety records, then build a script (S1) and a reusable data-access module with a menu CLI (S2).

## What was built
- **Data:** 16 sugarcane varieties from the MPKV (Mahatma Phule Krishi Vidyapeeth) sugarcane varieties PDF, hand-entered in `data/sample_records.json` and checked against the source. Each record has `id`, `variety_name`, `release_year`, `institute`, `recommended_seasons`, `cane_yield_t_ha`, `duration_months`, `key_traits`, `state` and `source_url`.
- **S1:** `day02_s1.py` (this folder) loads the records, prints them all, searches by keyword, and counts records per season and per institute.
- **S2:** the logic is refactored into a reusable package:
  - `app/records.py` has `load_records`, `search`, `count_by` and `get_by_id`.
  - `app/cli.py` is a menu-driven command line on top of those functions.
- Added a virtual environment, `requirements.txt` and `.gitignore`.
- Added the original MPKV PDF to the repo as the data source (`data/source/mpkv_sugarcane_varieties.pdf`).

## Files
| File | Location | Purpose |
|------|----------|---------|
| `day02_s1.py` | `day02/` | Standalone script for S1 |
| `records.py` | `app/` | Data access functions |
| `cli.py` | `app/` | Menu-driven command line |
| `sample_records.json` | `data/` | The 16 hand-entered records |
| `mpkv_sugarcane_varieties.pdf` | `data/source/` | Original source document |

`app/` is shared by later days, so its files stay there instead of moving into this folder.

## How to run
Run from the repository root:

```
python day02\day02_s1.py
python -m app.cli
```

CLI menu:

| Choice | Action |
|--------|--------|
| 1 | List all varieties |
| 2 | Search by keyword (name, season or traits) |
| 3 | Count varieties per season |
| 4 | Count varieties per institute |
| 5 | Get one variety by id (for example `V10`) |
| 0 | Exit |

Example keywords: `jaggery`, `saline`, `smut`, `drought`, `adsali`.

## Data notes
- **V13 (Phule 09057):** the PDF gives no cane yield, so `cane_yield_t_ha` is empty and the CLI shows "not given in source".
- **V16 (Phule 13007):** the PDF gives one yield for all seasons, stored under the key `all_seasons`.
- **V14 and V15:** the PDF lists a crop duration of 12 months, stored as `[12, 12]`.

## Source
https://mpkv.ac.in/Uploads/Research/09%20-%20Sugarcane_20230830095518.pdf