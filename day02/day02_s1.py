# day02_s1.py - S1: load the hand-entered records, print all, search by keyword, count per category.
import json

with open("data/sample_records.json", encoding="utf-8") as f:
    records = json.load(f)

print(f"Total records: {len(records)}\n")

# 1) print all
for r in records:
    print(f"{r['id']} | {r['variety_name']} | {r['release_year']} | {', '.join(r['recommended_seasons'])}")

# 2) search by keyword
keyword = input("\nSearch keyword (e.g. jaggery, saline, smut): ").strip().lower()
found = [r for r in records
         if keyword in (r["variety_name"] + " " + r["key_traits"]).lower()]
print(f"{len(found)} match(es) for '{keyword}':")
for r in found:
    print(f"  - {r['variety_name']}")

# 3) count per category (season and institute)
season_counts = {}
for r in records:
    for s in r["recommended_seasons"]:
        season_counts[s] = season_counts.get(s, 0) + 1
print("\nCount per season:", season_counts)

institute_counts = {}
for r in records:
    institute_counts[r["institute"]] = institute_counts.get(r["institute"], 0) + 1
print("Count per institute:", institute_counts)