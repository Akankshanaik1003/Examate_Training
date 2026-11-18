"""Season timeline for CaneMitra (Day 10).

Given a season and a planting date, work out:
  * the planting date,
  * the fertiliser split dates,
  * the harvest window (month by month).

IMPORTANT: the numbers below (duration per season, fertiliser split days,
harvest window of +/- 30 days) are PLACEHOLDER ASSUMPTIONS for the demo.
They have not been checked against the MPKV guide yet. Verify them and edit
the two dictionaries before showing this to a farmer.
"""

import calendar
from dataclasses import dataclass
from datetime import date, timedelta

SEASONS = ["adsali", "preseasonal", "suru"]

# Typical crop duration in months per Maharashtra season (assumption, verify).
# If your record has duration_months, pass it as `duration_months` instead.
DEFAULT_DURATION_MONTHS = {
    "adsali": 18,
    "preseasonal": 15,
    "suru": 12,
}

# Days after planting for each fertiliser split (assumption, verify).
FERTILISER_SPLIT_DAYS = {
    "adsali": [0, 45, 90, 135],
    "preseasonal": [0, 45, 90, 135],
    "suru": [0, 45, 90],
}

SPLIT_NAMES = ["Basal dose", "Split 2", "Split 3", "Split 4"]

HARVEST_WINDOW_DAYS = 30  # window = maturity date -/+ 30 days


@dataclass
class Stage:
    name: str
    start: date
    end: date
    kind: str  # "planting", "fertiliser", "growth" or "harvest"


def add_months(d: date, months: int) -> date:
    """Add whole months to a date without needing python-dateutil."""
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def month_list(start: date, end: date) -> list:
    """Month names between two dates, e.g. ['Jan 2028', 'Feb 2028', 'Mar 2028']."""
    months = []
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        months.append(f"{calendar.month_abbr[m]} {y}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return months


def build_timeline(season: str, planting_date: date, duration_months: int = None) -> dict:
    """Return the stages plus a summary for one season and planting date."""
    season = season.lower().strip()
    if season not in SEASONS:
        raise ValueError(f"Unknown season '{season}'. Use one of {SEASONS}.")

    months = duration_months or DEFAULT_DURATION_MONTHS[season]
    maturity = add_months(planting_date, months)
    harvest_start = maturity - timedelta(days=HARVEST_WINDOW_DAYS)
    harvest_end = maturity + timedelta(days=HARVEST_WINDOW_DAYS)

    stages = [Stage("Planting", planting_date, planting_date + timedelta(days=7), "planting")]

    for i, day in enumerate(FERTILISER_SPLIT_DAYS[season]):
        d = planting_date + timedelta(days=day)
        stages.append(Stage(SPLIT_NAMES[i], d, d + timedelta(days=7), "fertiliser"))

    stages.append(Stage("Crop growth", planting_date, harvest_start, "growth"))
    stages.append(Stage("Harvest window", harvest_start, harvest_end, "harvest"))

    return {
        "season": season,
        "planting_date": planting_date,
        "duration_months": months,
        "maturity_date": maturity,
        "harvest_start": harvest_start,
        "harvest_end": harvest_end,
        "harvest_months": month_list(harvest_start, harvest_end),
        "stages": stages,
    }


if __name__ == "__main__":
    # Quick check: python -m ui.timeline
    for s in SEASONS:
        t = build_timeline(s, date(2026, 11, 18))
        print(f"\n{s}: planted {t['planting_date']}, duration {t['duration_months']} months")
        for st in t["stages"]:
            print(f"  {st.kind:<10} {st.name:<15} {st.start} -> {st.end}")
        print("  harvest months:", ", ".join(t["harvest_months"]))
