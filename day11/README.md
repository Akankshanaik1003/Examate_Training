# Day 11 - Tests, lint and Docker

**Date:** Thu 19 Nov
**S1:** `tests/` with 8+ pytest tests (records, search, `/health`, `/ask` with a fake LLM, and the agent tool); `ruff check .` passes.
**S2:** `Dockerfile` + `.dockerignore` + `docker-compose.yml` so the CaneMitra API and UI start with `docker compose up`; README "Run with Docker".

## Files

| Path                    | What it does                                                                                       |
| ----------------------- | -------------------------------------------------------------------------------------------------- |
| `tests/conftest.py`     | Shared `client` fixture (FastAPI `TestClient`)                                                     |
| `tests/test_records.py` | `load_records`, `load_all_records`, `get_by_id` (found and missing)                                |
| `tests/test_search.py`  | Smart search: results, scores, `top_k`, empty query                                                |
| `tests/test_api.py`     | `/health`, `/records?limit=`, `/records/{id}`, 404, `/search`                                      |
| `tests/test_chat.py`    | `/ask` with a fake RAG function and a fake Chroma collection; empty question is rejected (422)     |
| `tests/test_agent.py`   | Agent loop with a fake LLM: `parse_action`, `format_steps`, tool call then answer, max steps       |
| `pyproject.toml`        | Settings for ruff (`ruff check .`) and pytest (`tests/` folder, repo root on the path)             |
| `requirements-dev.txt`  | `pytest`, `httpx` and `ruff` on top of `requirements.txt`                                          |
| `Dockerfile`            | One image for the API and the UI (CPU-only PyTorch)                                                |
| `.dockerignore`         | Keeps `.venv`, `.git`, `.env`, `data/chroma` and caches out of the build                           |
| `docker-compose.yml`    | Starts `api` (port 8000) and `ui` (port 8501)                                                      |

## Tests

```
pip install -r requirements-dev.txt
python -m pytest -v
```

23 tests. They never call Gemini or Groq and never download the embedding model: the LLM and the RAG function are replaced with fakes using `monkeypatch`.

## Lint

Run from the **repository root**:

```
ruff check .
```

It must print `All checks passed!`. Long lines are allowed (`E501` is ignored in `pyproject.toml`).

## Run with Docker

```
docker compose up --build
```

- API docs: http://localhost:8000/docs
- UI: http://localhost:8501 (it reaches the API at `http://api:8000` inside Docker)

Stop with `Ctrl+C`, then `docker compose down`.

How it is built:
- **CPU-only PyTorch** is installed first. The default Linux torch downloads about 1.5 GB of CUDA libraries a CPU container never uses; that download timed out the first two builds.
- **One image** (`canemitra:latest`) is built once and used by both services.
- **`./data` is mounted** into the containers, so they use your records, `chunks.json`, the Chroma index (`data/chroma`) and save `data/feedback.jsonl` on your PC.
- **`.env`** is passed in at run time and is never copied into the image.
- The embedding model is downloaded on the first `/ask` and kept in the `hf_cache` volume.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Build is very slow at "load build context" | `.dockerignore` is missing or in the wrong folder. It must be in the repo root. |
| `ReadTimeoutError` or `Name or service not known` while pip installs | Network drop. Run `docker compose up --build` again; downloaded packages are cached. |
| `/ask` says the index is empty (503) | Rebuild the index inside Docker: `docker compose run --rm api python -m app.vectorstore` |
| First `/ask` is slow | It downloads the embedding model once (needs internet); after that it is cached. |
| `/ask` fails on a key | `.env` is missing or its key names differ from `.env.example`. |
| `port is already allocated` | Stop your local `uvicorn` / `streamlit` first. |