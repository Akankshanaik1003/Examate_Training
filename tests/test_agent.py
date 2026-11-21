import json

from app.agent_loop import format_steps, parse_action, run_agent


def make_fake_llm(replies):
    """Fake LLM with the same (system, user) signature as generate. Returns the replies in order."""
    queue = list(replies)

    def fake(system, user):
        return queue.pop(0) if len(queue) > 1 else queue[0]

    return fake


# ---- parse_action (no LLM needed) ----

def test_parse_action_final():
    text = json.dumps({"action": "final", "answer": "Co 419 is good.", "citations": ["T01"]})
    action = parse_action(text)
    assert action["action"] == "final"
    assert action["citations"] == ["T01"]


def test_parse_action_tool_call():
    text = json.dumps({"action": "tool", "tool": "rag_search", "args": {"query": "saline"}})
    action = parse_action(text)
    assert action == {"action": "tool", "tool": "rag_search", "args": {"query": "saline"}}


def test_parse_action_handles_code_fence_and_extra_words():
    text = 'Sure! ```json\n{"action": "final", "answer": "ok", "citations": []}\n```'
    assert parse_action(text)["answer"] == "ok"


def test_parse_action_bad_output_becomes_final():
    action = parse_action("this is not json at all")
    assert action["action"] == "final"
    assert action["answer"] == "this is not json at all"


def test_format_steps_empty():
    assert "no tools called yet" in format_steps([])


# ---- run_agent with a fake LLM and a fake tool ----

def test_run_agent_final_answer_directly():
    llm = make_fake_llm([json.dumps({"action": "final", "answer": "I don't know.", "citations": []})])
    out = run_agent("anything", llm=llm)
    assert out["stopped"] == "final"
    assert out["answer"].startswith("I don't know")
    assert out["steps"] == []


def test_run_agent_calls_tool_then_answers(monkeypatch):
    monkeypatch.setattr("app.agent_loop.run_tool", lambda name, args: {"ok": True, "tool": name})
    llm = make_fake_llm([
        json.dumps({"action": "tool", "tool": "rag_search", "args": {"query": "saline"}}),
        json.dumps({"action": "final", "answer": "Use variety X.", "citations": ["T05"]}),
    ])
    out = run_agent("which variety for saline soil?", llm=llm)
    assert out["stopped"] == "final"
    assert len(out["steps"]) == 1
    assert out["steps"][0]["tool"] == "rag_search"
    assert out["citations"] == ["T05"]


def test_run_agent_stops_at_max_steps(monkeypatch):
    monkeypatch.setattr("app.agent_loop.run_tool", lambda name, args: {"ok": True})
    llm = make_fake_llm([json.dumps({"action": "tool", "tool": "rag_search", "args": {}})])
    out = run_agent("loop forever", max_steps=3, llm=llm)
    assert out["stopped"] == "max_steps"
    assert len(out["steps"]) == 3
    assert out["answer"].startswith("I don't know")