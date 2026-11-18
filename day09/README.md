# Day 9 - Agent with tools: hand-written loop, then LangGraph

**Task (Tue 17 Nov):** S1 build the agent tool in `app/tools.py` (`cane_harvest_window`: adds the crop duration in months for the chosen variety and season, taken from the records JSON, to the planting date with Python `datetime`; returns the earliest and latest harvest month), then `app/agent_loop.py`: a hand-written agent that can call the RAG search and this tool. S2 `app/graph.py` rebuilds it in LangGraph with memory + one approval step; `POST /agent`.

## Files

| Path | What it is |
|---|---|
| `app/tools.py` | `cane_harvest_window()`, `rag_search()`, the `TOOLS` registry and `run_tool()` (never raises, returns `{"error": ...}`) |
| `app/agent_loop.py` | hand-written agent: LLM replies with JSON (call a tool / final answer), loop runs the tool, max 5 steps |
| `app/graph.py` | the same agent in LangGraph: nodes `plan`, `approve`, `act`, `finish`; memory by `thread_id`; one approval step |
| `app/main.py` | adds `POST /agent` |

## cane_harvest_window

    cane_harvest_window("Co 419", "suru", "2026-12-15")
    -> duration 12-14 months, earliest_harvest "December 2027", latest_harvest "February 2028"

* Duration comes from the records: `duration_months` for the 16 MPKV records, the text "Duration 10 - 11 months" in `key_traits` for the 42 TNAU records.
* Month arithmetic uses only `datetime` and `calendar` (31 Jan + 1 month = 28/29 Feb).
* Unknown variety, a season the variety is not recommended for, or a bad date returns `{"error": ...}` so the agent can recover.

## How the hand-written agent works (S1)

1. Send the question and the tool results so far to the LLM.
2. The LLM returns `{"action": "tool", ...}` or `{"action": "final", ...}`.
3. For a tool action, run it, store the result, repeat. Stop on a final answer or after 5 steps.

## What LangGraph adds (S2)

* **Memory:** a checkpointer saves the state per `thread_id`; the same id on the next request gives the agent the earlier questions and answers. `MemorySaver` is in RAM, so memory is lost when the server restarts.
* **Approval step:** before `cane_harvest_window` runs, the graph pauses (`interrupt`) and `/agent` answers `awaiting_approval`. Send `approve: true` to run it or `false` to cancel. Change which tools need approval with `APPROVAL_TOOLS` in `.env`.

## Run

    pip install langgraph
    python -m app.vectorstore
    python -m app.tools
    python -m app.agent_loop "Which variety tolerates saline soil?"
    python -m app.agent_loop "When can I harvest Co 419 planted on 2026-12-15 in suru?"
    uvicorn app.main:app --reload

`POST /agent` (PowerShell, use the Swagger page at `/docs` if quoting is a problem):

    curl -X POST http://127.0.0.1:8000/agent -H "Content-Type: application/json" -d "{\"question\": \"When can I harvest Co 419 planted on 2026-12-15 in suru?\"}"
    curl -X POST http://127.0.0.1:8000/agent -H "Content-Type: application/json" -d "{\"thread_id\": \"PASTE_ID\", \"approve\": true}"
    curl -X POST http://127.0.0.1:8000/agent -H "Content-Type: application/json" -d "{\"thread_id\": \"PASTE_ID\", \"question\": \"And for Co 740?\"}"