"""explore.py - 3 facts about the CaneMitra records, using pandas (Day 4, S2).

Run from the repo root:  python -m analysis.explore
"""
import pandas as pd

from app.records import load_all_records


def build_frame() -> pd.DataFrame:
    rows = []
    for r in load_all_records():
        rows.append({
            "id": r["id"],
            "variety": r["variety_name"],
            "source": "MPKV (Maharashtra)" if r["id"].startswith("V") else "TNAU (Tamil Nadu)",
            "seasons": r["recommended_seasons"],
            "yields": r["cane_yield_t_ha"],
            "traits": r["key_traits"].lower(),
        })
    return pd.DataFrame(rows)


def main():
    df = build_frame()
    print(f"Total records: {len(df)}  ({df['source'].value_counts().to_dict()})\n")

    # Fact 1: best single-season yield per variety -> top 3 overall
    df["best_yield"] = df["yields"].apply(lambda d: max(d.values()) if d else None)
    top = df.dropna(subset=["best_yield"]).nlargest(3, "best_yield")[["id", "variety", "best_yield"]]
    print("Fact 1 - Top 3 highest cane yields (t/ha):")
    print(top.to_string(index=False), "\n")

    # Fact 2: average Maharashtra yield per season (adsali vs preseasonal vs suru)
    mpkv = df[df["source"].str.startswith("MPKV")]
    long = mpkv.explode("seasons")
    long["season_yield"] = long.apply(
        lambda r: r["yields"].get(r["seasons"], r["yields"].get("all_seasons")), axis=1)
    avg = long.dropna(subset=["season_yield"]).groupby("seasons")["season_yield"].mean().round(1)
    print("Fact 2 - Average yield per Maharashtra season (t/ha):")
    print(avg.to_string(), "\n")

    # Fact 3: how many varieties mention drought tolerance, per source
    df["drought"] = df["traits"].str.contains("drought")
    print("Fact 3 - Varieties whose notes mention drought, per source:")
    print(df.groupby("source")["drought"].sum().to_string())


if __name__ == "__main__":
    main()