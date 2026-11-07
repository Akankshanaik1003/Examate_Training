# day01_menu.py - while-loop menu for CaneMitra.

SAMPLE_QUESTIONS = [
    "How many months does Phule 265 take if I plant suru season?",
    "Which sugarcane variety is recommended for jaggery making in Maharashtra?",
    "What is the planting time for preseasonal sugarcane in Maharashtra?",
]


def season_check():
    """Rule check from the domain: which season does a planting month fall in?
    Month ranges below are typical Maharashtra values - verify against the MPKV PDF later."""
    month = int(input("Planting month number (1-12): "))
    if month in (7, 8):
        print("Adsali season (long duration, about 18 months).")
    elif month in (10, 11):
        print("Preseasonal (about 15 months).")
    elif month in (1, 2):
        print("Suru season (about 12 months).")
    else:
        print("Outside the usual adsali / preseasonal / suru planting windows.")


while True:
    print("\n--- CaneMitra Menu ---")
    print("1. About CaneMitra")
    print("2. Sample questions")
    print("3. Season rule check")
    print("0. Exit")
    choice = input("Enter choice: ").strip()

    if choice == "1":
        print("CaneMitra answers sugarcane questions for Maharashtra farmers "
              "and works out the harvest window for your planting date.")
    elif choice == "2":
        for i, q in enumerate(SAMPLE_QUESTIONS, start=1):
            print(f"{i}) {q}")
    elif choice == "3":
        try:
            season_check()
        except ValueError:
            print("Please enter a number like 10.")
    elif choice == "0":
        print("Goodbye!")
        break
    else:
        print("Invalid choice. Please enter 1, 2, 3 or 0.")