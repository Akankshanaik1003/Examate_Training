import json

rows = [json.loads(line) for line in open("logs/requests.jsonl", encoding="utf-8")]
miss = [r for r in rows if not r["cache_hit"]]
hit = [r for r in rows if r["cache_hit"]]


def avg(xs):
    return round(sum(xs) / len(xs), 1) if xs else 0


print("requests:", len(rows))
print("avg latency, LLM call (ms):", avg([r["latency_ms"] for r in miss]))
print("avg latency, cache hit (ms):", avg([r["latency_ms"] for r in hit]))
print("avg tokens per request (estimated):", avg([r["tokens"] for r in miss]))
print("cache hit rate %:", round(100 * len(hit) / len(rows), 1) if rows else 0)