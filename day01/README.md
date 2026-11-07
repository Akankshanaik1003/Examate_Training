# Day 1 - Project idea and interactive menu

**Task (D1, Wed 4 Nov):** define the project (product, user, problem, data source), then build a project-card script and a menu loop.

## Project card
- **Project:** CaneMitra
- **Domain:** Agriculture (sugarcane, Maharashtra)
- **Product:** answers sugarcane questions for Maharashtra farmers using MPKV Rahuri, DSD and TNAU guides, and works out the harvest window for a planting date.
- **User:** a sugarcane farmer with 4 acres of medium-deep black soil near Kopargaon, deciding whether to plant Phule 265 as preseasonal or suru cane in October.
- **Problem:** answers differ by season (adsali, preseasonal, suru) and by state, and units vary (kg/ha vs kg/acre, t/ha).
- **Data source:** PDF (MPKV, DSD) and HTML (TNAU Agritech).

## Files
| File | What it does |
|------|--------------|
| `day01_intro.py` | Prints the project card using variables and f-strings, then asks the user's name and question with `input()`. |
| `day01_menu.py` | While-loop menu: 1 About CaneMitra, 2 Sample questions, 3 Season rule check (planting month to adsali / preseasonal / suru), 0 Exit. Non-numeric months are handled with `try/except`. |

## How to run
Run from the repository root:

```
python day01\day01_intro.py
python day01\day01_menu.py
```

## Notes
- The season month ranges in the rule check are typical Maharashtra values. They still need to be verified against the MPKV PDF before being shown as farmer guidance.