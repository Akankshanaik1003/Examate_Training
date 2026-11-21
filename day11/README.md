# Day 11 - Tests, lint and Docker

**Date:** Thu 19 Nov
**S1:** `tests/` with 8+ pytest tests (records, search, `/health`, `/ask` with a fake LLM, and the agent tool); `ruff check .` passes.
**S2:** `Dockerfile` + `.dockerignore` + `docker-compose.yml` so the CaneMitra API and UI start with `docker compose up`; README "Run with Docker".

## Files

| Path                    | What it does                                                                                              |
| ----------------------- | --------------------------------------------------------------------------------------------------------- |
| `tests/__init__.py`     | Empty file                                                                                                |
| `tests/conftest.py`     | Test helpers: API client, fake LLM, fake Chroma index, fake agent graph (no key, no network, no model)    |
| `tests/test_records.py` | `load_records`, `load_all_records`, `get_by_id`, `search`, `count_by`, `SmartSearch`                       |
| `tests/test_tools.py`   | Agent tool `cane_harvest_window`, `add_months`, `run_tool`                                                |
| `tests/test_api.py`     | `/health`, `/records`, `/search`, `/questions`, `/ask` (fake LLM + index), `/agent` (approval flow)       |
| `pytest.ini`            | pytest settings                                                                                           |
| `ruff.toml`             | Lint settings                                                                                             |
| `Dockerfile`            | One image for the API and the UI (CPU-only PyTorch)                                                       |
| `.dockerignore`         | Keeps `.venv`, `.git`, `.env`, `data/chroma` and caches out of the build                                  |
| `docker-compose.yml`    | Starts `api` (port 8000) and `ui` (port 8501)                                                             |

## Tests

```
python -m pytest -v
```

42 tests. They never call Gemini or Groq and never download the embedding model: `conftest.py` replaces `app.rag.generate`, the Chroma lookup and the agent's LLM with fakes. Several tests check the fake was (or was not) called, for example a low-score question must say "I don't know" without calling the LLM, and an invented citation must be rejected.

## Lint

Run from the **repository root** (not from inside `tests/`):

```
ruff check . --fix
ruff check .
```

The last command must print `All checks passed!`. `--fix` only adds missing end-of-file newlines and sorts imports in your older files.

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
| `ReadTimeoutError` or `Name or service not known` while pip installs | Network drop. Run `docker compose up --build` again; downloaded packages are cached, so it continues where it stopped. |
| `/ask` says the index is empty (503) | Rebuild the index inside Docker: `docker compose run --rm api python -m app.vectorstore` |
| First `/ask` is slow | It downloads the embedding model once (needs internet); after that it is cached. |
| `/ask` fails on a key | `.env` is missing or its key names differ from `.env.example`. |
| `port is already allocated` | Stop your local `uvicorn` / `streamlit` first. |