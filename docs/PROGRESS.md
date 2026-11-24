# CaneMitra: progress

Final status of the 14-day plan. `[x]` means done and in the repository; `[ ]` means open (see "Open items").

## Days

- [x] Day 1: project card, intro script, interactive menu
- [x] Day 2: 16 hand-entered MPKV records, search/count script, CLI
- [x] Day 3: `Record` dataclass, downloader, ingest of the TNAU page (42 records)
- [x] Day 4: FastAPI service, pandas analysis, TF-IDF smart search
- [x] Day 5: how LLMs work, 10 user questions, Checkpoint 1 (`checkpoint-1`)
- [x] Day 6: LLM wrapper (Gemini / Groq), `POST /chat`, prompts v1/v2
- [x] Day 7: chunking, embeddings, Chroma, `GET /search/semantic`
- [x] Day 8: RAG `POST /ask` with citations and "I don't know"; 15-question evaluation
- [x] Day 9: agent with tools, LangGraph memory and approval step, `POST /agent`
- [x] Day 10: Streamlit UI and season timeline (Checkpoint 2, `checkpoint-2`)
- [x] Day 11: 28 pytest tests, ruff, Docker and docker compose
- [x] Day 12: GitHub Actions CI with badge, merged pull request, live deploy on Render
- [x] Day 13: input limits, injection check, cache, latency and token logging, measured production notes, README rewrite, resume bullets
- [x] Day 14: interview preparation in `docs/interview.md` (60-second pitch, hardest-problem story, 10 answers) and this file

## Results

| Metric | Result |
|---|---|
| RAG evaluation, config B (15 questions) | 9/15 (60%), retrieval hit 9/12, 3/3 correct "I don't know" |
| Tests | 28 passing, `ruff check .` clean |
| Avg latency, LLM call vs cache hit | 10683.9 ms vs 0.0 ms (under 1 ms) |
| Avg tokens per request (estimated) | 250.9 |
| Cache hit rate (13 requests) | 23.1 % |
| Prompt-injection test | blocked with HTTP 400 |

## Open items

These are known gaps, listed so nothing is hidden. None blocks the 14-day plan.

- [ ] Add the demo video link to the README (needs the recorded video)
- [ ] Improve retrieval: config B still misses 3 of 12 answerable questions
- [ ] Verify the season timeline numbers against the MPKV guide (they are placeholders in `ui/timeline.py`)
- [ ] Read real token counts from the provider instead of estimating
- [ ] Apply the guard and a cache to `/agent`
- [ ] Add a real third source in `app/fetch.py`
- [ ] Use the saved thumbs feedback to improve prompts

## Release

The final state of the project is tagged `final`.