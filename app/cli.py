
#S2
"""cli.py - command-line menu for CaneMitra. Run from the repo root:  python -m app.cli"""
from app.records import load_records, search, count_by, get_by_id


def show(r):
    yields = ", ".join(f"{k}: {v} t/ha" for k, v in r["cane_yield_t_ha"].items()) or "not given in source"
    print(f"{r['id']} | {r['variety_name']} ({r['release_year']}) | {r['institute']}")
    print(f"    Seasons : {', '.join(r['recommended_seasons'])}")
    print(f"    Yield   : {yields}")
    print(f"    Traits  : {r['key_traits']}")
    print(f"    Source  : {r['source_url']}")


def main():
    records = load_records()
    while True:
        print("\n--- CaneMitra Records ---")
        print("1. List all varieties")
        print("2. Search by keyword")
        print("3. Count per season")
        print("4. Count per institute")
        print("5. Get by id")
        print("0. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            for r in records:
                print(f"{r['id']} - {r['variety_name']} ({r['release_year']})")
        elif choice == "2":
            hits = search(records, input("Keyword: "))
            print(f"{len(hits)} match(es)")
            for r in hits:
                show(r)
        elif choice == "3":
            print(count_by(records, "recommended_seasons"))
        elif choice == "4":
            print(count_by(records, "institute"))
        elif choice == "5":
            r = get_by_id(records, input("Id (e.g. V10): "))
            show(r) if r else print("No record with that id.")
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()