# day01_intro.py - prints the CaneMitra project card, then asks the user's name and question.


project_name = "CaneMitra"
domain = "Agriculture (Sugarcane, Maharashtra)"
product = ("Answers sugarcane questions for Maharashtra farmers using MPKV Rahuri, "
           "DSD and TNAU guides, and works out the harvest window for your planting date.")
user_desc = ("Sugarcane farmer with 4 acres of medium-deep black soil near Kopargaon "
             "deciding whether to plant Phule 265 as preseasonal or suru cane this October.")
problem = ("Answers differ by season (adsali, preseasonal, suru) and by state, "
             "and units vary (kg/ha vs kg/acre, t/ha).")
data_source = "PDF (MPKV, DSD) + HTML (TNAU Agritech)"


print("=" * 60)
print(f"  PROJECT CARD: {project_name}")
print("=" * 60)
print(f"Domain      : {domain}")
print(f"Product     : {product}")
print(f"User        : {user_desc}")
print(f"Problem     : {problem}")
print(f"Data source : {data_source}")
print("=" * 60)


name = input("What is your name? ").strip()
question = input(f"Hello {name}! What is your sugarcane question? ").strip()

print()
print(f"Thanks, {name}. You asked: \"{question}\"")
print(f"{project_name} will be able to answer this from real guides in a later version.")