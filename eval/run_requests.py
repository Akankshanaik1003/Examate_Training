import time

import requests

URL = "http://127.0.0.1:8000/ask"
QUESTIONS = [
    "Which sugarcane variety suits saline soil?",
    "Which variety is best for drought conditions?",
    "Which variety gives the highest cane yield?",
    "Which varieties are recommended for the adsali season?",
    "Which varieties are suited to Maharashtra?",
    "Which variety has high sugar content?",
    "Which early maturing variety is recommended?",
    "Which variety resists red rot?",
    "Which varieties suit the suru season?",
    "What is the duration of Co 86032?",
]

for q in QUESTIONS + QUESTIONS[:3]:
    r = requests.post(URL, json={"question": q, "top_k": 5}, timeout=120)
    print(r.status_code, q)
    time.sleep(1)