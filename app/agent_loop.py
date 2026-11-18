"""agent_loop.py - Day 9, S1: a hand-written agent (no framework).

The loop:
    1. Show the model the question + what the tools returned so far.
    2. The model replies with JSON: either call a tool, or give the final answer.
    3. If it called a tool, run it, add the result to the notes, go back to 1.
    4. Stop on a final answer or after MAX_STEPS (so it can never loop forever).

Use:
    from app.agent_loop import run_agent
    result = run_agent("When can I harvest Co 419 planted on 15 Dec 2026 in suru?")
    print(result["answer"])

Run from the repo root:   python -m app.agent_loop "your question"
"""
import json
import re
import sys
from datetime import date

from app.llm import LLMError, generate
from app.tools import run_tool, tool_descriptions

MAX_STEPS = 5
RESULT_LIMIT = 2500  # characters of a tool result shown to the model

SYSTEM_PROMPT = """You are CaneMitra, a friendly sugarcane assistant for farmers in Maharashtra.
Today's date is {today}.

You can use these tools:
{tools}

Reply with ONE JSON object and nothing else. Two shapes are allowed.

Call a tool:
{{"action": "tool", "tool": "<tool name>", "args": {{...}}}}

Give the final answer:
{{"action": "final", "answer": "<short answer in simple words>", "citations": ["<chunk id>", ...]}}

Rules:
1. Use only facts from tool results. Never use outside knowledge.
2. For questions about varieties, traits, soil, disease, yield or seasons, call rag_search first.
3. For "when can I harvest" questions call cane_harvest_window. If the farmer did not give the variety,
   season or planting date, do not guess: give a final answer that asks for the missing item.
   If the farmer says "today", use today's date above.
4. If a tool returns an "error", read it and fix your next call, or tell the farmer what is wrong.
5. If the tool results do not contain the answer, the answer must start with: I don't know
6. "citations" lists the ids of the rag_search chunks you used (empty list if none).
"""


def build_system_prompt() -> str:
    return SYSTEM_PROMPT.format(today=date.today().isoformat(), tools=tool_descriptions())


def parse_action(text: str) -> dict:
    """Turn the model's text into an action dict. Never raises; bad output becomes a final answer."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        data = json.loads(cleaned)
    except ValueError:
        # The model may add words before/after the JSON: decode the first {...} object we can find.
        data = None
        start = cleaned.find("{")
        if start != -1:
            try:
                data, _ = json.JSONDecoder().raw_decode(cleaned[start:])
            except ValueError:
                data = None
        if data is None:
            return {"action": "final", "answer": text.strip(), "citations": []}
    if not isinstance(data, dict):
        return {"action": "final", "answer": text.strip(), "citations": []}

    if data.get("action") == "tool" and isinstance(data.get("tool"), str):
        args = data.get("args")
        return {"action": "tool", "tool": data["tool"], "args": args if isinstance(args, dict) else {}}

    citations = data.get("citations")
    return {
        "action": "final",
        "answer": str(data.get("answer", "")).strip() or "I don't know.",
        "citations": [str(c) for c in citations] if isinstance(citations, list) else [],
    }


def format_steps(steps: list[dict]) -> str:
    """Notes shown to the model: every tool call so far and what it returned."""
    if not steps:
        return "(no tools called yet)"
    lines = []
    for i, s in enumerate(steps, 1):
        result = json.dumps(s["result"], ensure_ascii=False)
        if len(result) > RESULT_LIMIT:
            result = result[:RESULT_LIMIT] + " ...(cut)"
        lines.append(f"{i}. called {s['tool']} with {json.dumps(s['args'], ensure_ascii=False)}\n   result: {result}")
    return "\n".join(lines)


def build_user_message(question: str, steps: list[dict], history: list[dict] | None = None) -> str:
    parts = []
    if history:  # used by the LangGraph version (Day 9, S2) for memory
        talk = "\n".join(f"Farmer: {h['question']}\nCaneMitra: {h['answer']}" for h in history[-5:])
        parts.append(f"Earlier in this chat:\n{talk}")
    parts.append(f"Question: {question}")
    parts.append(f"Tool calls so far:\n{format_steps(steps)}")
    parts.append("What is your next JSON reply?")
    return "\n\n".join(parts)


def call_llm(llm, system: str, user: str) -> str:
    """Call the LLM. Groq/Gemini JSON mode returns HTTP 400 when the model's output is not strict JSON;
    in that case ask again without JSON mode (parse_action can handle fences and extra words)."""
    try:
        return llm(system, user)
    except LLMError as e:
        if "HTTP 400" in str(e) and llm is generate:
            return generate(system, user, json_mode=False)
        raise


def run_agent(question: str, max_steps: int = MAX_STEPS, llm=generate) -> dict:
    """Run the loop. `llm` is generate by default; tests pass a fake with the same (system, user) signature.

    Returns {"question", "answer", "citations", "steps", "stopped"}.
    "stopped" is "final" (normal) or "max_steps" (the model kept calling tools).
    Raises LLMError if the model call fails.
    """
    system = build_system_prompt()
    steps: list[dict] = []

    for _ in range(max_steps):
        action = parse_action(call_llm(llm, system, build_user_message(question, steps)))

        if action["action"] == "final":
            return {"question": question, "answer": action["answer"], "citations": action["citations"],
                    "steps": steps, "stopped": "final"}

        result = run_tool(action["tool"], action["args"])
        steps.append({"tool": action["tool"], "args": action["args"], "result": result})

    return {
        "question": question,
        "answer": "I don't know. I could not finish this within the allowed number of steps.",
        "citations": [],
        "steps": steps,
        "stopped": "max_steps",
    }


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "When can I harvest Co 419 planted on 2026-12-15 in the suru season?"
    try:
        out = run_agent(q)
    except LLMError as e:
        sys.exit(f"LLM error: {e}")
    for i, s in enumerate(out["steps"], 1):
        print(f"[step {i}] {s['tool']} {s['args']}")
    print("\nANSWER:", out["answer"])
    if out["citations"]:
        print("CITATIONS:", ", ".join(out["citations"]))