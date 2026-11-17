"""prompt_compare.py - run your 10 user questions through prompt v1 and v2 and write eval/prompt_compare.md (Day 6, S2).

Run from the repo root:  python -m eval.prompt_compare            (provider from LLM_PROVIDER in .env)
                         python -m eval.prompt_compare groq       (force Groq)
What it does:
  1. Checks the key with ONE small call. If it fails, it tries the other provider that has a key.
  2. Runs the 20 calls (10 questions x v1/v2) with the SAME provider, pausing between calls.
  3. Saves good answers in eval/.compare_cache.json, so a re-run only repeats the failed ones
     (useful when the free tier says 429 / timeout).
  4. Writes eval/prompt_compare.md. The LAST lines of that file say "STATUS: SUCCESS" or "STATUS: ERROR" and why.
The verdict (Better / Why columns and "My verdict") is for you to write by reading the answers; a re-run keeps it.
"""
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from app.chat import PROMPTS, chat
from app.llm import LLMError, check_provider, configured_providers, load_env
from app.records import load_all_records
from app.smart_search import SmartSearch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "eval" / "prompt_compare.md"
CACHE = ROOT / "eval" / ".compare_cache.json"
PAUSE = {"gemini": 7, "groq": 2}  # seconds between calls: Gemini free tier allows ~10 requests/minute
PLACEHOLDER = "_Fill in after reading the table"
STATUS_MARK = "## Run status"


def load_questions() -> list[tuple[int, str, str]]:
    """Read (number, question, 'can data answer') from the table in docs/user_questions.md."""
    rows = []
    for line in (ROOT / "docs" / "user_questions.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[0].isdigit():
            rows.append((int(cells[0]), cells[1], re.sub(r"\*", "", cells[3])))
    return rows


def prompts_hash() -> str:
    """Changes when any prompt file changes, so old cached answers are not reused for new prompts."""
    h = hashlib.sha1()
    for f in sorted(PROMPTS.glob("*.md")):
        h.update(f.read_bytes())
    return h.hexdigest()[:10]


def cell(text: str) -> str:
    return text.replace("\n", " ").replace("|", "/")


def pick_provider(requested: str | None) -> tuple[str | None, list[str]]:
    """Return (working provider or None, list of messages explaining what was tried)."""
    notes = []
    wanted = requested or os.environ.get("LLM_PROVIDER", "gemini").lower()
    order = [wanted] + [p for p in ("gemini", "groq") if p != wanted]
    for name in order:
        if name not in configured_providers():
            notes.append(f"{name}: no key in .env")
            continue
        print(f"Checking {name} key ...")
        ok, msg = check_provider(name)
        notes.append(msg)
        if ok:
            return name, notes
    return None, notes


def old_verdict() -> str | None:
    """Keep what you wrote under 'My verdict' on a re-run."""
    if not OUT.exists():
        return None
    text = OUT.read_text(encoding="utf-8")
    if "## My verdict" not in text:
        return None
    part = text.split("## My verdict", 1)[1].split(STATUS_MARK, 1)[0].strip("\n- ")
    return None if (not part.strip() or PLACEHOLDER in part) else part.strip()


def write_report(lines: list[str], verdict: str | None, status: str) -> None:
    lines += ["", "## My verdict", "", verdict or f"{PLACEHOLDER}: which prompt is better, and what did Q6 and Q10 (not in the data) show?_", ""]
    lines += ["---", "", STATUS_MARK, "", status, ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")


def header() -> list[str]:
    return [
        "# Prompt comparison: v1 vs v2",
        "",
        "- **v1** (`prompts/system_v1.md`): short role prompt, asks for JSON, no rule about what to do when the records do not answer.",
        "- **v2** (`prompts/system.md`): adds rules: use only the records, say \"not in my records\" instead of guessing, quote exact numbers, mark TNAU as Tamil Nadu, same language as the question, defined confidence levels.",
        "",
        "Same 10 questions from `docs/user_questions.md`, same retrieved records, same model. Answers below were produced by running `python -m eval.prompt_compare`.",
        "",
    ]


def main() -> None:
    load_env()
    requested = sys.argv[1].lower() if len(sys.argv) > 1 else None
    questions = load_questions()
    total = 2 * len(questions)
    verdict = old_verdict()
    stamp = datetime.now().strftime("%d-%m-%Y %H:%M")

    provider, notes = pick_provider(requested)
    if provider is None:
        status = (
            f"**STATUS: ERROR** ({stamp}) - the API test call failed, so 0 of {total} answers were produced.\n\n"
            + "\n".join(f"- {n}" for n in notes)
            + "\n\nFix: if it says 'not set' or 'no key', put a real key in `.env` (see `.env.example`). "
            "If it says 429 or timed out, wait one minute (free-tier limit) or switch `LLM_PROVIDER`. "
            "Run `python check_key.py` until it says SUCCESS, then run `python -m eval.prompt_compare` again."
        )
        write_report(header(), verdict, status)
        print(status)
        sys.exit(1)

    model = os.environ.get("GEMINI_MODEL" if provider == "gemini" else "GROQ_MODEL", "default")
    print(f"Using provider: {provider} ({model})")
    search = SmartSearch(load_all_records())
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    ph = prompts_hash()
    pause = PAUSE.get(provider, 5)
    failed: list[str] = []

    def answer(n: int, q: str, version: str) -> dict:
        key = f"{ph}|{provider}|{model}|{version}|{n}"
        if key in cache:
            return cache[key]
        try:
            a = chat(q, search.search(q, top_k=3), version=version, provider=provider)
            cache[key] = a
            CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        except LLMError as e:
            a = {"answer": f"ERROR: {e}", "confidence": "-", "follow_up": ""}
            failed.append(f"Q{n} {version}: {e}")
        time.sleep(pause)
        return a

    lines = header() + [
        f"Provider used: **{provider}** (`{model}`), run on {stamp}.",
        "",
        "| # | Question | Data can answer? | v1 answer (confidence) | v2 answer (confidence) | Better | Why |",
        "|---|----------|------------------|------------------------|------------------------|--------|-----|",
    ]
    for n, q, can in questions:
        a1, a2 = answer(n, q, "v1"), answer(n, q, "v2")
        lines.append(
            f"| {n} | {cell(q)} | {can} | {cell(a1['answer'])} ({a1['confidence']}) | {cell(a2['answer'])} ({a2['confidence']}) |  |  |"
        )
        print(f"Q{n} done")

    if failed:
        status = (
            f"**STATUS: ERROR** ({stamp}) - {len(failed)} of {total} answers failed with {provider}.\n\n"
            + "\n".join(f"- {f}" for f in failed[:6])
            + ("\n- ..." if len(failed) > 6 else "")
            + "\n\nFix: wait one minute (free-tier limit) and run `python -m eval.prompt_compare` again. "
            "Good answers are saved, so only the failed ones are repeated."
        )
    else:
        status = f"**STATUS: SUCCESS** ({stamp}) - all {total} answers were produced with {provider} (`{model}`), no errors."
    write_report(lines, verdict, status)
    print(f"wrote {OUT}")
    print(status)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()