# Day 5 - How LLMs work, user questions and Checkpoint 1

**Task (D5, Thu 12 Nov):**
- Write `docs/how_llms_work.md` in my own words with 1 diagram.
- Add 10 real CaneMitra user questions (start with the 6 from my card); Q6 must be one the data cannot answer.
- **Checkpoint 1:** run the FastAPI service, show `/docs`, explain one function. Tag `checkpoint-1`.

## Where the Day 5 files are
The Day 5 documents live in the shared `docs/` folder at the repository root, not in this folder. This README only points to them.

| Task part | File | Path |
|-----------|------|------|
| LLM explainer with 1 diagram | How LLMs work, with a Mermaid diagram | [`docs/how_llms_work.md`](../docs/how_llms_work.md) |
| 10 user questions | Table of questions, who asks, and whether the data can answer | [`docs/user_questions.md`](../docs/user_questions.md) |
| Checkpoint 1 | Screenshot of the `/docs` page of the running API | [`docs/checkpoint1_docs.png`](../docs/checkpoint1_docs.png) |
| Checkpoint 1 | The function I explain (`ask()`) | [`app/main.py`](../app/main.py) |

## What is in each file

**`docs/how_llms_work.md`** explains in simple words what an LLM is, tokens, embeddings, the Transformer and attention, training vs inference, the context window and hallucination. The last section connects it to CaneMitra: an LLM does not know our 58 records, so we search the records first and give the matches to the model (RAG), or let it say "I don't know". The diagram shows where CaneMitra's own data enters the model.

**`docs/user_questions.md`** lists 10 questions a farmer might ask. For each one it says whether CaneMitra's data can answer it and which records or gap are involved.
- **Q6** is the question the data cannot answer (fertilizer dose per acre). The records only describe variety traits.
- **Q10** (market price / FRP) is also not in the data.
- **Q8 and Q9** are only partly answerable (planting months and harvest date are not built yet).

## Checkpoint 1: run the API and show `/docs`
Run from the repository root:

```
.venv\Scripts\activate
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. The screenshot is saved as [`docs/checkpoint1_docs.png`](../docs/checkpoint1_docs.png). Two requests are tried on `POST /questions`:

| Request body | Result |
|--------------|--------|
| `{"question": "saline soil"}` | Returns a saline-tolerant variety (for example Phule 265) with its source |
| A question the data cannot answer (Q6, fertilizer dose) | Still returns the "closest" record, because search matches words, not meaning |

## The function I explain: `ask()` in `app/main.py`
`ask()` handles `POST /questions`.

- **Input:** a JSON body with one `question` string, checked by the `Question` model.
- **Steps:**
  1. Rejects an empty question with a 422 error.
  2. Calls `SEARCH.search(question, top_k=3)`. `SmartSearch` compares the question with all 58 records using TF-IDF and cosine similarity.
  3. If no record shares a word with the question, it returns "No matching variety found in the records."
  4. Otherwise it builds the answer from the best match.
- **Output:** the question, an answer made from the best variety's name and traits, the `source_url`, and the top 3 matches with scores.
- **Why CaneMitra needs it:** it is the point where a farmer's question meets the data, and the `source_url` lets the farmer check the answer.

## Limits found during Day 5
- Search matches words, not meaning, so a question that the data cannot answer can still return a close-looking record. This is the hallucination risk described in `docs/how_llms_work.md`.
- Next step: return "not in our data" when the best score is low.

