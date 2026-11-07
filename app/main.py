"""main.py - FastAPI service for CaneMitra (Day 4, S1).

Run from the repo root:  uvicorn app.main:app --reload
Docs (auto-generated):   http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.records import get_by_id, load_all_records
from app.smart_search import SmartSearch

app = FastAPI(title="CaneMitra API", version="0.4.0")

RECORDS = load_all_records()
SEARCH = SmartSearch(RECORDS)


class Question(BaseModel):
    question: str


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