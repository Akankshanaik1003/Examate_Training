"""Save thumbs up / thumbs down feedback to data/feedback.jsonl (Day 10)."""

import json
from datetime import datetime
from pathlib import Path

FEEDBACK_FILE = Path(__file__).resolve().parent.parent / "data" / "feedback.jsonl"


def save_feedback(rating: str, question: str, answer: str, endpoint: str, sources: list) -> None:
    """Append one feedback row. rating is 'up' or 'down'."""
    if rating not in ("up", "down"):
        raise ValueError("rating must be 'up' or 'down'")
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "rating": rating,
        "endpoint": endpoint,
        "question": question,
        "answer": answer,
        "sources": sources,
    }
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_feedback() -> list:
    """Read all saved feedback rows (empty list if none yet)."""
    if not FEEDBACK_FILE.exists():
        return []
    rows = []
    with open(FEEDBACK_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows
