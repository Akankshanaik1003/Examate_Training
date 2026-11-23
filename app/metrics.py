import json
import os
import time

LOG_FILE = "logs/requests.jsonl"


def estimate_tokens(text):
    """Rough estimate: about 4 characters per token."""
    return max(1, len(text) // 4)


def log_request(endpoint, question, latency_ms, tokens, cache_hit):
    os.makedirs("logs", exist_ok=True)
    row = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "endpoint": endpoint,
        "question": question[:80],
        "latency_ms": round(latency_ms, 1),
        "tokens": tokens,
        "cache_hit": cache_hit,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")