"""graph.py - Day 9, S2: the same agent rebuilt in LangGraph, with memory and one approval step.

Graph (each box is a node):

    START -> plan --final answer--> finish -> END
              |  ^
     tool call|  |(tool result / rejection)
              v  |
        [approval needed?]
          yes -> approve --approved--> act --+
                    |                        |
                    +--rejected--> plan      +--> plan
          no  -----------------------> act

* plan    : asks the LLM for the next action (same prompt and parser as agent_loop.py).
* approve : the ONE approval step. interrupt() pauses the graph and hands the pending tool call to the
            caller; it continues when the caller resumes with {"approve": true/false}.
* act     : runs the tool (app/tools.py).
* finish  : saves the question and answer into `history`.

Memory: a checkpointer saves the state after every node, keyed by thread_id. Asking again with the same
thread_id gives the agent the earlier questions and answers (`history`). MemorySaver keeps this in RAM,
so it is lost when the server restarts.

Only tools listed in APPROVAL_TOOLS wait for approval (default: cane_harvest_window).
Set APPROVAL_TOOLS in .env (comma separated), e.g. APPROVAL_TOOLS=cane_harvest_window,rag_search
"""
import os
import uuid
from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.agent_loop import (
    MAX_STEPS,
    build_system_prompt,
    build_user_message,
    call_llm,
    parse_action,
)
from app.llm import generate, load_env
from app.tools import run_tool

load_env()

APPROVAL_TOOLS = {t.strip() for t in os.environ.get("APPROVAL_TOOLS", "cane_harvest_window").split(",") if t.strip()}


class AgentState(TypedDict):
    question: str           # this turn's question
    history: list[dict]     # earlier turns [{"question", "answer"}]; kept by the checkpointer = memory
    steps: list[dict]       # tool calls made in this turn
    pending: dict | None    # tool call waiting to run: {"tool", "args"}
    answer: str
    citations: list[str]
    stopped: str            # "final" or "max_steps"


def build_graph(llm=generate, checkpointer=None):
    """Compile the agent graph. `llm` is generate by default; tests pass a fake."""

    def plan(state: AgentState) -> dict:
        if len(state["steps"]) >= MAX_STEPS:
            return {"pending": None, "stopped": "max_steps", "citations": [],
                    "answer": "I don't know. I could not finish this within the allowed number of steps."}
        action = parse_action(call_llm(llm, build_system_prompt(),
                                       build_user_message(state["question"], state["steps"], state.get("history", []))))
        if action["action"] == "final":
            return {"pending": None, "answer": action["answer"], "citations": action["citations"],
                    "stopped": "final"}
        return {"pending": {"tool": action["tool"], "args": action["args"]}}

    def needs_approval(state: AgentState) -> str:
        if state["pending"] is None:
            return "finish"
        return "approve" if state["pending"]["tool"] in APPROVAL_TOOLS else "act"

    def approve(state: AgentState) -> dict:
        # Nothing may happen before interrupt(): this node runs again from the top when the graph resumes.
        decision = interrupt({"tool": state["pending"]["tool"], "args": state["pending"]["args"]})
        approved = bool(decision.get("approve")) if isinstance(decision, dict) else bool(decision)
        if approved:
            return {}
        rejected = {"tool": state["pending"]["tool"], "args": state["pending"]["args"],
                    "result": {"error": "The farmer did not approve this tool call. Do not call it again; "
                                        "answer with what you already know or ask what to change."}}
        return {"steps": state["steps"] + [rejected], "pending": None}

    def after_approve(state: AgentState) -> str:
        return "act" if state["pending"] is not None else "plan"

    def act(state: AgentState) -> dict:
        call = state["pending"]
        result = run_tool(call["tool"], call["args"])
        return {"steps": state["steps"] + [{"tool": call["tool"], "args": call["args"], "result": result}],
                "pending": None}

    def finish(state: AgentState) -> dict:
        return {"history": state.get("history", []) + [{"question": state["question"], "answer": state["answer"]}]}

    g = StateGraph(AgentState)
    g.add_node("plan", plan)
    g.add_node("approve", approve)
    g.add_node("act", act)
    g.add_node("finish", finish)

    g.add_edge(START, "plan")
    g.add_conditional_edges("plan", needs_approval, {"finish": "finish", "approve": "approve", "act": "act"})
    g.add_conditional_edges("approve", after_approve, {"act": "act", "plan": "plan"})
    g.add_edge("act", "plan")
    g.add_edge("finish", END)

    return g.compile(checkpointer=checkpointer or MemorySaver())


# ---- helpers used by POST /agent ------------------------------------------------------------------------

def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _snapshot(graph, thread_id: str) -> dict:
    """Describe where the thread is: finished, or paused waiting for approval."""
    snap = graph.get_state(_config(thread_id))
    values = snap.values
    if snap.next:  # paused at the approval node
        asked = snap.tasks[0].interrupts[0].value
        return {"thread_id": thread_id, "status": "awaiting_approval", "pending": asked, "answer": None,
                "citations": [], "steps": values.get("steps", [])}
    return {"thread_id": thread_id, "status": "done", "pending": None, "answer": values.get("answer", ""),
            "citations": values.get("citations", []), "steps": values.get("steps", [])}


def is_waiting(graph, thread_id: str) -> bool:
    return bool(graph.get_state(_config(thread_id)).next)


def ask(graph, question: str, thread_id: str | None = None) -> dict:
    """Start a new turn. Returns status "done" or "awaiting_approval"."""
    thread_id = thread_id or uuid.uuid4().hex[:12]
    if is_waiting(graph, thread_id):
        raise ValueError("This thread is waiting for approval. Send approve true or false first.")
    graph.invoke({"question": question, "steps": [], "pending": None, "answer": "", "citations": [],
                  "stopped": ""}, _config(thread_id))
    return _snapshot(graph, thread_id)


def resume(graph, thread_id: str, approve: bool) -> dict:
    """Answer the pending approval question and let the graph continue."""
    if not is_waiting(graph, thread_id):
        raise ValueError("Nothing is waiting for approval on this thread.")
    graph.invoke(Command(resume={"approve": approve}), _config(thread_id))
    return _snapshot(graph, thread_id)