"""chat.py - build the prompt, call the LLM and return a structured answer (Day 6, S2)."""
import json
import re
from pathlib import Path

from app.llm import generate

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"
CONFIDENCE = {"high", "medium", "low"}
FIELDS = ("variety_name", "recommended_seasons", "cane_yield_t_ha", "duration_months", "key_traits", "state", "source_url")


def load_prompt(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text(encoding="utf-8")


def system_prompt_for(version: str) -> str:
    """'v2' (default) is prompts/system.md; 'v1' is the first, looser prompt kept for comparison."""
    return load_prompt("system_v1" if version == "v1" else "system")


def format_records(matches: list[dict]) -> str:
    lines = []
    for r in matches:
        lines.append(f"- [{r['id']}] " + "; ".join(f"{f}: {r[f]}" for f in FIELDS if r.get(f) not in (None, "", [], {})))
    return "\n".join(lines)


def parse_reply(text: str) -> dict:
    """Turn the model's text into {answer, confidence, follow_up}; never raises."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            raise ValueError
    except ValueError:
        return {"answer": text.strip(), "confidence": "low", "follow_up": ""}
    confidence = str(data.get("confidence", "low")).lower()
    return {
        "answer": str(data.get("answer", "")).strip(),
        "confidence": confidence if confidence in CONFIDENCE else "low",
        "follow_up": str(data.get("follow_up", "") or "").strip(),
    }


def chat(question: str, matches: list[dict], version: str = "v2", provider: str | None = None) -> dict:
    """Ask the LLM to answer from the matched records. Returns answer, confidence, follow_up, sources."""
    if matches:
        task = load_prompt("task_answer").format(question=question, records=format_records(matches))
    else:
        task = load_prompt("task_no_match").format(question=question)
    reply = parse_reply(generate(system_prompt_for(version), task, provider=provider))
    reply["sources"] = sorted({m["source_url"] for m in matches if m.get("source_url")})
    return reply