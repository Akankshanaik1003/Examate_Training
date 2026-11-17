# Day 8 - RAG answers with citations and a small evaluation

**Task (Mon 16 Nov):** S1 `app/rag.py` + `POST /ask` answers CaneMitra questions from retrieved chunks with citations, and says "I don't know" when the chunks do not cover the question. S2 `eval/eval_set.json` (15 rows) + `eval/run_eval.py`, run with 2 configs (chunk size / top-k), winner table in the main README.

## Files

| Path | What it is |
|---|---|
| `app/rag.py` | `retrieve()` and `answer_question()`: top-k chunks, grounded prompt, citations, "I don't know" gate |
| `app/main.py` | adds `POST /ask` (body: `question`, optional `top_k` 1-10) |
| `eval/eval_set.json` | 15 questions: 12 answerable (with expected keywords), 3 that must get "I don't know" |
| `eval/run_eval.py` | runs config A and B, scores them, writes `eval/results.json`, `eval/results.md` and the README table |
| `eval/results.md`, `eval/results.json` | output of the last run |

## How "I don't know" works

1. If the best chunk's cosine score is below `RAG_MIN_SCORE` (default 0.25, can be set in `.env`), the API answers "I don't know" without calling the LLM.
2. Otherwise the prompt tells the model to answer only from the chunks and to start with "I don't know" if they do not contain the answer.

## Run

    python -m app.vectorstore
    uvicorn app.main:app --reload
    curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d "{\"question\": \"Which variety tolerates saline soil?\"}"
    python eval\run_eval.py --check
    python eval\run_eval.py --write-readme