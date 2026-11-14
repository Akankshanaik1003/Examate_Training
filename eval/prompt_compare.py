"""prompt_compare.py - run your 10 user questions through prompt v1 and v2 and write eval/prompt_compare.md (Day 6, S2).

Run from the repo root:  python -m eval.prompt_compare
Needs a working key in .env. The verdict columns are left blank for you to fill in by reading the answers.
"""
import re
import time
from pathlib import Path

from app.chat import chat
from app.llm import LLMError
from app.records import load_all_records
from app.smart_search import SmartSearch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "eval" / "prompt_compare.md"


def load_questions() -> list[tuple[int, str, str]]:
    """Read (number, question, 'can data answer') from the table in docs/user_questions.md."""
    rows = []
    for line in (ROOT / "docs" / "user_questions.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[0].isdigit():
            rows.append((int(cells[0]), cells[1], re.sub(r"\*", "", cells[3])))
    return rows


def run(search: SmartSearch, question: str, version: str) -> dict:
    try:
        return chat(question, search.search(question, top_k=3), version=version)
    except LLMError as e:
        return {"answer": f"ERROR: {e}", "confidence": "-", "follow_up": ""}


def cell(text: str) -> str:
    return text.replace("\n", " ").replace("|", "/")


def main() -> None:
    search = SmartSearch(load_all_records())
    questions = load_questions()
    lines = [
        "# Prompt comparison: v1 vs v2",
        "",
        "- **v1** (`prompts/system_v1.md`): short role prompt, asks for JSON, no rule about what to do when the records do not answer.",
        "- **v2** (`prompts/system.md`): adds rules: use only the records, say \"not in my records\" instead of guessing, quote exact numbers, mark TNAU as Tamil Nadu, same language as the question, defined confidence levels.",
        "",
        "Same 10 questions from `docs/user_questions.md`, same retrieved records, same model. Answers below were produced by running `python -m eval.prompt_compare`.",
        "",
        "| # | Question | Data can answer? | v1 answer (confidence) | v2 answer (confidence) | Better | Why |",
        "|---|----------|------------------|------------------------|------------------------|--------|-----|",
    ]
    for n, q, can in questions:
        a1, a2 = run(search, q, "v1"), run(search, q, "v2")
        lines.append(
            f"| {n} | {cell(q)} | {can} | {cell(a1['answer'])} ({a1['confidence']}) | {cell(a2['answer'])} ({a2['confidence']}) |  |  |"
        )
        print(f"Q{n} done")
        time.sleep(1)  # stay under free-tier rate limits
    lines += ["", "## My verdict", "", "_Fill in after reading the table: which prompt is better, and what did Q6 and Q10 (not in the data) show?_", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()