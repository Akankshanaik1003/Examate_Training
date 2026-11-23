"""main.py - FastAPI service for CaneMitra (Day 4, S1).

Run from the repo root:  uvicorn app.main:app --reload
Docs (auto-generated):   http://127.0.0.1:8000/docs
"""
import json
import os
import time

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app import cache, guard, metrics
from app.chat import chat
from app.graph import ask as agent_ask
from app.graph import build_graph
from app.graph import resume as agent_resume
from app.llm import LLMError
from app.rag import answer_question
from app.records import get_by_id, load_all_records
from app.smart_search import SmartSearch
from app.vectorstore import get_collection
from app.vectorstore import search as semantic_chunks

app = FastAPI(title="CaneMitra API", version="0.9.0")

GUARDED_PATHS = {"/chat", "/ask"}


@app.middleware("http")
async def production_layer(request: Request, call_next):
    """Day 13: input limits + injection check, cache, and latency/token logging for /chat and /ask."""
    if request.method != "POST" or request.url.path not in GUARDED_PATHS:
        return await call_next(request)

    path = request.url.path
    body_bytes = await request.body()
    try:
        data = json.loads(body_bytes or b"{}")
    except ValueError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    question = str(data.get("question", ""))

    ok, msg = guard.check_input(question)
    if not ok:
        return JSONResponse(status_code=400, content={"detail": msg})

    # Skip cache and log file while pytest runs, so the tests stay independent.
    testing = "PYTEST_CURRENT_TEST" in os.environ
    key = f"{path}|{question.strip().lower()}|{data.get('top_k')}|{data.get('prompt_version')}"

    start = time.perf_counter()
    if not testing:
        cached = cache.get(key)
        if cached is not None:
            metrics.log_request(path, question, (time.perf_counter() - start) * 1000, 0, True)
            return JSONResponse(content=cached)

    async def receive():
        return {"type": "http.request", "body": body_bytes, "more_body": False}

    response = await call_next(Request(request.scope, receive))
    resp_body = b"".join([chunk async for chunk in response.body_iterator])
    ms = (time.perf_counter() - start) * 1000

    if response.status_code == 200 and not testing and question.strip():
        try:
            cache.put(key, json.loads(resp_body))
        except ValueError:
            pass
        tokens = metrics.estimate_tokens(question + resp_body.decode("utf-8", "ignore"))
        metrics.log_request(path, question, ms, tokens, False)

    return Response(
        content=resp_body,
        status_code=response.status_code,
        headers={k: v for k, v in response.headers.items() if k.lower() != "content-length"},
        media_type=response.media_type,
    )


RECORDS = load_all_records()
SEARCH = SmartSearch(RECORDS)


class Question(BaseModel):
    question: str


class ChatRequest(BaseModel):
    question: str
    prompt_version: str = "v2"  # "v1" = first prompt, "v2" = grounded prompt (prompts/system.md)


class AskRequest(BaseModel):
    question: str
    top_k: int = 3  # how many chunks to retrieve (1-10)


@app.get("/health")
def health():
    return {"status": "ok", "records": len(RECORDS)}


@app.get("/records")
def list_records(limit: int = Query(10, ge=1, le=200)):
    return RECORDS[:limit]


@app.get("/records/{record_id}")
def record_by_id(record_id: str):
    record = get_by_id(RECORDS, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No record with id {record_id}")
    return record


@app.get("/search")
def search(q: str = Query(..., min_length=1), top_k: int = Query(5, ge=1, le=20)):
    results = SEARCH.search(q, top_k)
    return {"query": q, "count": len(results), "results": results}


@app.post("/questions")
def ask(body: Question):
    """Answer a farmer's question by returning the best matching varieties and their source."""
    if not body.question.strip():
        raise HTTPException(status_code=422, detail="question must not be empty")
    matches = SEARCH.search(body.question, top_k=3)
    if not matches:
        return {"question": body.question, "answer": "No matching variety found in the records.", "matches": []}
    best = matches[0]
    return {
        "question": body.question,
        "answer": f"Closest match: {best['variety_name']}. {best['key_traits']}",
        "source_url": best["source_url"],
        "matches": matches,
    }


@app.get("/search/semantic")
def search_semantic(q: str = Query(..., min_length=2), k: int = 3):
    if get_collection().count() == 0:
        raise HTTPException(status_code=503, detail="Index is empty. Run: python -m app.vectorstore")
    return {"query": q, "results": semantic_chunks(q, k)}

@app.post("/chat")
def chat_endpoint(body: ChatRequest):
    """Day 6: find the best records, then let the LLM write a grounded answer as JSON."""
    if not body.question.strip():
        raise HTTPException(status_code=422, detail="question must not be empty")
    if body.prompt_version not in ("v1", "v2"):
        raise HTTPException(status_code=422, detail="prompt_version must be v1 or v2")
    matches = SEARCH.search(body.question, top_k=3)
    try:
        return chat(body.question, matches, version=body.prompt_version)
    except LLMError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/ask")
def ask_rag(body: AskRequest):
    """Day 8: answer from retrieved chunks with citations; says "I don't know" when the chunks do not cover it."""
    if not body.question.strip():
        raise HTTPException(status_code=422, detail="question must not be empty")
    if not 1 <= body.top_k <= 10:
        raise HTTPException(status_code=422, detail="top_k must be between 1 and 10")
    if get_collection().count() == 0:
        raise HTTPException(status_code=503, detail="Index is empty. Run: python -m app.vectorstore")
    try:
        return answer_question(body.question, top_k=body.top_k)
    except LLMError as e:
        raise HTTPException(status_code=503, detail=str(e))


class AgentRequest(BaseModel):
    question: str = ""             # a new question (leave empty when you are only answering an approval)
    thread_id: str | None = None   # same id = same conversation (memory); omit to start a new one
    approve: bool | None = None    # true/false answers a pending approval


_AGENT_GRAPH = None


def get_agent_graph():
    """Build the LangGraph agent once and reuse it, so its memory survives between requests."""
    global _AGENT_GRAPH
    if _AGENT_GRAPH is None:
        _AGENT_GRAPH = build_graph()
    return _AGENT_GRAPH


@app.post("/agent")
def agent_endpoint(body: AgentRequest):
    """Day 9: agent with tools (RAG search + harvest window), memory per thread_id and an approval step.

    1. {"question": "..."}                      -> status "done", or "awaiting_approval" with the pending tool call
    2. {"thread_id": "...", "approve": true}    -> continues; false cancels that tool call
    """
    graph = get_agent_graph()
    try:
        if body.approve is not None:
            if not body.thread_id:
                raise HTTPException(status_code=422, detail="thread_id is required to answer an approval")
            return agent_resume(graph, body.thread_id, body.approve)
        if not body.question.strip():
            raise HTTPException(status_code=422, detail="question must not be empty")
        return agent_ask(graph, body.question, body.thread_id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except LLMError as e:
        raise HTTPException(status_code=503, detail=str(e))