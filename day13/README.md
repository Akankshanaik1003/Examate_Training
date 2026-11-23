# Day 13 - Production notes and CaneMitra README

**S1 (production basics)**
- `app/guard.py`: input limit (500 characters) and a keyword prompt-injection check, returns HTTP 400.
- `app/cache.py`: in-memory cache (1 hour) for repeated `/ask` and `/chat` questions.
- `app/metrics.py`: writes latency, estimated tokens and cache hit per request to `logs/requests.jsonl` (not committed).
- `app/main.py`: a middleware applies all three to `POST /ask` and `POST /chat`.
- `tests/test_guard.py`: injection and length tests. `eval/injection_test.py` checks the live server.
- `eval/run_requests.py` sends 13 requests; `python -m analysis.summarize_logs` prints the numbers used in the README.

**S2 (README and resume)**
- README rewritten to explain the problem, show the architecture (Mermaid), link the demo video and show results.
- `docs/resume.md`: 3 resume bullets.