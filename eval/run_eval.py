"""run_eval.py - Day 8, S2: score 2 RAG configs on eval/eval_set.json and write the winner table.

Run from the repo root:
  python eval\\run_eval.py --check            # no LLM: are the expected keywords really in data/chunks.json?
  python eval\\run_eval.py --retrieval-only   # no LLM: retrieval hits + top scores only
  python eval\\run_eval.py                    # full run (30 LLM calls), writes eval/results.json and eval/results.md
  python eval\\run_eval.py --write-readme     # full run + put the table in README.md between EVAL markers

Each config re-chunks the text of data/chunks.json (grouped by source+page) into windows of
`chunk_words` words, embeds them into a temporary in-memory Chroma collection and retrieves `top_k`.
Your real index in data/chroma is never touched.

Changes in this version:
  - "With citations" counts only answers where the MODEL really cited a retrieved chunk (res["model_cited"]).
  - Rows that failed with an LLM error are counted and reported, so rate limits do not look like wrong answers.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import chromadb  # noqa: E402

from app import rag  # noqa: E402
from app.embed import embed_texts  # noqa: E402
from app.llm import LLMError  # noqa: E402

EVAL_SET = ROOT / "eval" / "eval_set.json"
CHUNKS_FILE = ROOT / "data" / "chunks.json"
RESULTS_JSON = ROOT / "eval" / "results.json"
RESULTS_MD = ROOT / "eval" / "results.md"
README = ROOT / "README.md"
START, END = "<!-- EVAL:START -->", "<!-- EVAL:END -->"

# Edit these configs if you want to compare other sizes (run --check to see your current average chunk size).
# Task asks for 2 configs. To separate the effect of chunk size from top-k, you can add a third one:
#   {"name": "C", "chunk_words": 250, "overlap": 40, "top_k": 3},
CONFIGS = [
    {"name": "A", "chunk_words": 120, "overlap": 20, "top_k": 3},
    {"name": "B", "chunk_words": 250, "overlap": 40, "top_k": 5},
]
SLEEP = float(os.environ.get("EVAL_SLEEP", "2"))  # seconds between LLM calls (free tiers are rate limited)


def has_word(text: str, word: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(word.lower()) + r"(?!\w)", text.lower()) is not None


def has_any(text: str, words: list[str]) -> bool:
    return any(has_word(text, w) for w in words)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")[:20] or "doc"


def rechunk(chunks: list[dict], size: int, overlap: int) -> list[dict]:
    groups: dict = {}
    for c in chunks:
        groups.setdefault((c["source"], c.get("page") or 0, c.get("title") or ""), []).append(c["text"])
    out, step = [], max(1, size - overlap)
    for g, ((source, page, title), texts) in enumerate(groups.items()):
        words = " ".join(texts).split()
        for n, start in enumerate(range(0, len(words), step)):
            window = words[start:start + size]
            if not window:
                break
            out.append({"id": f"{slug(source)}-p{page}-{g}-{n}", "text": " ".join(window),
                        "source": source, "page": page, "title": title})
            if start + size >= len(words):
                break
    return out


def build_collection(name: str, chunks: list[dict]):
    client = chromadb.EphemeralClient()
    try:
        client.delete_collection(name)
    except Exception:
        pass
    collection = client.create_collection(name, metadata={"hnsw:space": "cosine"})
    for start in range(0, len(chunks), 64):
        batch = chunks[start:start + 64]
        collection.add(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            embeddings=embed_texts([c["text"] for c in batch]).tolist(),
            metadatas=[{"source": c["source"], "page": c["page"], "title": c["title"]} for c in batch],
        )
    return collection


def run_config(cfg: dict, rows: list[dict], chunks: list[dict], retrieval_only: bool, provider) -> dict:
    new_chunks = rechunk(chunks, cfg["chunk_words"], cfg["overlap"])
    print(f"\n== Config {cfg['name']}: {cfg['chunk_words']} words, top-{cfg['top_k']} -> {len(new_chunks)} chunks")
    collection = build_collection(f"eval_{cfg['name'].lower()}", new_chunks)
    details = []
    for row in rows:
        answerable = row["type"] == "answerable"
        kws = row.get("expected_keywords", [])
        d = {"id": row["id"], "type": row["type"], "question": row["question"],
             "answer": "", "idk": False, "answer_ok": False, "retrieval_hit": None,
             "cited_ok": None, "top_score": 0.0, "seconds": 0.0, "error": ""}
        t0 = time.time()
        try:
            if retrieval_only:
                hits = rag.retrieve(row["question"], cfg["top_k"], collection)
                d["top_score"] = hits[0]["score"] if hits else 0.0
                d["idk"] = d["top_score"] < rag.MIN_SCORE  # what the score gate alone would do
                d["retrieval_hit"] = has_any(" ".join(h["text"] for h in hits), kws) if answerable else None
                d["answer_ok"] = d["idk"] if not answerable else False
            else:
                res = rag.answer_question(row["question"], cfg["top_k"], collection, provider)
                d["answer"], d["idk"] = res["answer"], res["idk"]
                d["top_score"] = res["retrieved"][0]["score"] if res["retrieved"] else 0.0
                if answerable:
                    got = " ".join(h["text"] for h in rag.retrieve(row["question"], cfg["top_k"], collection))
                    d["retrieval_hit"] = has_any(got, kws)
                    d["answer_ok"] = (not d["idk"]) and has_any(res["answer"], kws)
                    # honest citation check: the model itself must have cited a retrieved chunk
                    d["cited_ok"] = (not d["idk"]) and bool(res.get("model_cited", False))
                else:
                    d["answer_ok"] = d["idk"]
        except LLMError as e:
            d["error"] = str(e)[:200]
        d["seconds"] = round(time.time() - t0, 2)
        if retrieval_only:
            mark = "n/a" if answerable else ("ok " if d["answer_ok"] else "BAD")  # answerable rows are not scored here
        else:
            mark = "ERR" if d["error"] else ("ok " if d["answer_ok"] else "BAD")
        print(f"  {row['id']} {row['type']:<12} {mark} top={d['top_score']:.2f} idk={d['idk']} {d['seconds']}s {d['error']}")
        details.append(d)
        if not retrieval_only and d["top_score"] >= rag.MIN_SCORE:
            time.sleep(SLEEP)

    ans = [d for d in details if d["type"] == "answerable"]
    un = [d for d in details if d["type"] != "answerable"]
    summary = {
        "name": cfg["name"], "chunk_words": cfg["chunk_words"], "top_k": cfg["top_k"], "chunks": len(new_chunks),
        "retrieval_hit": sum(bool(d["retrieval_hit"]) for d in ans),
        "answer_ok": sum(d["answer_ok"] for d in ans),
        "idk_ok": sum(d["answer_ok"] for d in un),
        "cited": sum(bool(d["cited_ok"]) for d in ans),
        "errors": sum(1 for d in details if d["error"]),
        "n_ans": len(ans), "n_un": len(un), "n": len(details),
        "avg_seconds": round(sum(d["seconds"] for d in details) / max(1, len(details)), 2),
    }
    summary["overall"] = round((summary["answer_ok"] + summary["idk_ok"]) / max(1, summary["n"]), 3)
    return {"summary": summary, "details": details}


def pct(a: int, b: int) -> str:
    return f"{a}/{b} ({round(100 * a / b) if b else 0}%)"


def winner_of(results: list[dict]) -> dict:
    return max((r["summary"] for r in results),
               key=lambda s: (s["overall"], s["retrieval_hit"], -s["avg_seconds"]))


def summary_table(results: list[dict], retrieval_only: bool) -> str:
    win = winner_of(results)["name"]
    lines = ["| Config | Chunk size | Top-k | Chunks | Retrieval hit | Answer correct | Correct \"I don't know\" | With citations | Overall | Avg sec/question |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        s = r["summary"]
        name = f"**{s['name']} (winner)**" if s["name"] == win else s["name"]
        correct = "n/a (retrieval only)" if retrieval_only else pct(s["answer_ok"], s["n_ans"])
        idk = pct(s["idk_ok"], s["n_un"])
        cited = "n/a" if retrieval_only else pct(s["cited"], s["n_ans"])
        overall = "n/a" if retrieval_only else pct(s["answer_ok"] + s["idk_ok"], s["n"])
        lines.append(f"| {name} | {s['chunk_words']} words | {s['top_k']} | {s['chunks']} | "
                     f"{pct(s['retrieval_hit'], s['n_ans'])} | {correct} | {idk} | {cited} | {overall} | {s['avg_seconds']} |")
    return "\n".join(lines)


def detail_table(results: list[dict]) -> str:
    head = "| Row | Type | Question | " + " | ".join(f"{r['summary']['name']}" for r in results) + " |"
    lines = [head, "|---|---|---|" + "---|" * len(results)]
    for i, d in enumerate(results[0]["details"]):
        cells = []
        for r in results:
            row = r["details"][i]
            cells.append("ERROR" if row["error"] else ("pass" if row["answer_ok"] else "FAIL"))
        lines.append(f"| {d['id']} | {d['type']} | {d['question']} | {' | '.join(cells)} |")
    return "\n".join(lines)


def error_note(results: list[dict]) -> str:
    parts = [f"config {r['summary']['name']}: {r['summary']['errors']}" for r in results if r["summary"]["errors"]]
    if not parts:
        return ""
    return ("WARNING: some rows failed with an LLM error (" + ", ".join(parts) + "). "
            "They are counted as FAIL. Check the \"error\" fields in eval/results.json, "
            "then re-run with a bigger EVAL_SLEEP (for example $env:EVAL_SLEEP=5 in PowerShell).")


def readme_block(results: list[dict], retrieval_only: bool) -> str:
    win = winner_of(results)
    cfgs = "; ".join(f"**{r['summary']['name']}** = {r['summary']['chunk_words']}-word chunks, top-{r['summary']['top_k']}" for r in results)
    return (f"Eval set: `eval/eval_set.json` (15 questions: 12 answerable, 3 that must get \"I don't know\"). "
            f"Configs: {cfgs}. Run with `python eval\\run_eval.py`.\n\n"
            f"{summary_table(results, retrieval_only)}\n\n"
            f"**Winner: config {win['name']}** ({win['chunk_words']}-word chunks, top-{win['top_k']}). "
            f"Per-question results are in `eval/results.md`.")


def write_readme(block: str) -> None:
    text = README.read_text(encoding="utf-8") if README.exists() else ""
    wrapped = f"{START}\n{block}\n{END}"
    if START in text and END in text:
        text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: wrapped, text, flags=re.S)
    else:
        text = text.rstrip() + f"\n\n## Day 8 - RAG answers and evaluation\n\n{wrapped}\n"
    README.write_text(text, encoding="utf-8")


def check(rows: list[dict], chunks: list[dict]) -> None:
    sizes = [len(c["text"].split()) for c in chunks]
    print(f"{len(chunks)} chunks in data/chunks.json, average {sum(sizes) // max(1, len(sizes))} words, max {max(sizes)}.")
    corpus = " ".join(c["text"] for c in chunks)
    bad = 0
    for r in rows:
        if r["type"] != "answerable":
            continue
        if not has_any(corpus, r["expected_keywords"]):
            bad += 1
            print(f"  NOT FOUND in corpus: {r['id']} {r['expected_keywords']}  -> change the keyword or the question")
    print("All answerable rows have at least one keyword in the corpus." if not bad else f"{bad} row(s) need fixing.")
    types = [r["type"] for r in rows]
    print(f"Rows: {len(rows)} ({types.count('answerable')} answerable, {types.count('unanswerable')} unanswerable).")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate eval_set.json against data/chunks.json (no LLM)")
    ap.add_argument("--retrieval-only", action="store_true", help="skip the LLM; score retrieval only")
    ap.add_argument("--write-readme", action="store_true", help="put the table in README.md")
    ap.add_argument("--provider", default=None, help="gemini or groq (default: LLM_PROVIDER in .env)")
    args = ap.parse_args()

    rows = json.loads(EVAL_SET.read_text(encoding="utf-8"))
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    if args.check:
        check(rows, chunks)
        return

    results = [run_config(cfg, rows, chunks, args.retrieval_only, args.provider) for cfg in CONFIGS]
    RESULTS_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    note = error_note(results)
    md = (f"# Day 8 eval results\n\n{summary_table(results, args.retrieval_only)}\n\n"
          + (f"{note}\n\n" if note else "")
          + f"## Per question\n\n{detail_table(results)}\n")
    RESULTS_MD.write_text(md, encoding="utf-8")
    print("\n" + summary_table(results, args.retrieval_only))
    if note:
        print("\n" + note)
    print(f"\nWinner: config {winner_of(results)['name']}. Saved eval/results.json and eval/results.md")
    if args.write_readme:
        write_readme(readme_block(results, args.retrieval_only))
        print("README.md updated between the EVAL markers.")


if __name__ == "__main__":
    main()