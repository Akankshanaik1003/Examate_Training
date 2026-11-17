"""Day 7: run the 10 questions through semantic search and record the hits."""
import json
from pathlib import Path

from app.embed import embed_texts, search

chunks = json.loads(Path("data/chunks.json").read_text(encoding="utf-8"))
vectors = embed_texts([c["text"] for c in chunks])
questions = [q.strip() for q in Path("eval/questions.txt").read_text(encoding="utf-8").splitlines() if q.strip()]

lines = ["# Day 7 - Semantic search results", "", f"{len(chunks)} chunks, top 3 hits per question.", ""]
for number, question in enumerate(questions, start=1):
    lines += [f"## Q{number}. {question}", ""]
    for rank, hit in enumerate(search(question, chunks, vectors, k=3), start=1):
        snippet = hit["text"][:200].replace("\n", " ")
        lines.append(f"{rank}. score {hit['score']:.3f} | {hit['source']} | page {hit['page']} | {hit['title']}")
        lines.append(f"   > {snippet}...")
    lines += ["", "Relevant hit in top 3: YES / NO (fill by hand)", ""]

Path("eval/search_results.md").write_text("\n".join(lines), encoding="utf-8")
print("Wrote eval/search_results.md")