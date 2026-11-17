"""main.py - FastAPI service for CaneMitra (Day 4, S1).

Run from the repo root:  uvicorn app.main:app --reload
Docs (auto-generated):   http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.vectorstore import get_collection, search as semantic_chunks

from app.chat import chat
from app.llm import LLMError
from app.rag import answer_question
from app.records import get_by_id, load_all_records
from app.smart_search import SmartSearch

app = FastAPI(title="CaneMitra API", version="0.8.0")

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