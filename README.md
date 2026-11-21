# CaneMitra

CaneMitra (Mitra = friend) is a sugarcane question-answering project for farmers, students and advisors. It collects sugarcane variety records and guide text from agricultural university sources, cleans them into one format, and serves them through a command line, a web API (keyword search, semantic search, RAG answers with citations, and an agent with tools) and a Streamlit chat with a season timeline. Tests, lint and Docker are set up.

**Status:** Days 1-11 are done. Tags: `week-1` (Days 1-4), `checkpoint-1` (Day 5), `checkpoint-2` (Day 10).

![CaneMitra UI](docs/day10_ui.png)

## Day-wise progress

Each day has its own folder with a README that explains the task and lists the exact path of every file. Code used by several days lives in the shared `app/`, `analysis/`, `eval/`, `docs/`, `tests/`, `ui/` and `data/` folders.

| Day    | Folder                                                                                       | What was built                                                                                        |
| ------ | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Day 1  | [`day01/`](https://github.com/Akankshanaik1003/Examate_Training/blob/main/day01/README.md)   | Project card, intro script and interactive menu                                                       |
| Day 2  | [`day02/`](https://github.com/Akankshanaik1003/Examate_Training/blob/main/day02/README.md)   | 16 hand-entered MPKV records, search/count script, reusable data functions and CLI                    |
| Day 3  | [`day03/`](https://github.com/Akankshanaik1003/Examate_Training/blob/main/day03/README.md)   | `Record` dataclass, downloader with error handling, ingest of the TNAU page into `data/records.json`  |
| Day 4  | [`day04/`](https://github.com/Akankshanaik1003/Examate_Training/blob/main/day04/README.md)   | FastAPI service, pandas analysis, TF-IDF smart search                                                 |
| Day 5  | [`day05/`](https://github.com/Akankshanaik1003/Examate_Training/blob/main/day05/README.md)   | How LLMs work (with diagram), 10 user questions, Checkpoint 1                                         |
| Day 6  | [`day06/`](https://github.com/Akankshanaik1003/Examate_Training/blob/main/day06/README.md)   | LLM provider wrapper, `POST /chat`, prompts, prompt comparison                                        |
| Day 7  | [`day07/`](https://github.com/Akankshanaik1003/Examate_Training/blob/main/day07/README.md)   | Chunking, embeddings, Chroma vector store, `GET /search/semantic`                                     |
| Day 8  | [`day08/`](https://github.com/Akankshanaik1003/Examate_Training/blob/main/day08/README.md)   | RAG: `POST /ask` with citations and "I don't know", 15-question evaluation of 2 configs               |
| Day 9  | [`day09/`](https://github.com/Akankshanaik1003/Examate_Training/blob/main/day09/README.md)   | Agent with tools: harvest-window tool, hand-written loop, LangGraph version, `POST /agent`            |
| Day 10 | [`day10/`](https://github.com/Akankshanaik1003/Examate_Training/blob/main/day10/README.md)   | Streamlit chat UI: calls `/ask` or `/agent`, citations, thumbs up/down, season timeline bar           |
| Day 11 | [`day11/`](https://github.com/Akankshanaik1003/Examate_Training/blob/main/day11/README.md)   | 42 pytest tests (fake LLM), ruff lint, Docker and docker compose                                      |

### Day 1 - Project idea and interactive menu

- Defined the project card: product, user, problem and data source.
- `day01/day01_intro.py` prints the card with f-strings and asks the user's name and question.
- `day01/day01_menu.py` is a while-loop menu with sample questions and a planting-month season check.

### Day 2 - Records, data access and CLI

- Hand-entered **16 varieties** from the MPKV sugarcane PDF into `data/sample_records.json`, each checked against the source.
- `day02/day02_s1.py` prints, searches and counts the records.
- `app/records.py` (load, search, count, get by id) and `app/cli.py` (menu CLI).
- Added a virtual environment, `requirements.txt` and `.gitignore`.

### Day 3 - Fetching and ingesting real data

- `app/models.py`: `Record` dataclass.
- `app/fetch.py`: downloads documents into `data/raw/` with `requests`, a 20 second timeout and error handling.
- `app/ingest.py`: cleans the TNAU page into **42 records** in `data/records.json`, skipping bad rows with `try/except`.

### Day 4 - API, analysis and smart search

- `app/main.py`: FastAPI service with `/health`, `/records`, `/records/{id}`, `/search` and `/questions`.
- `app/smart_search.py`: TF-IDF + cosine similarity ranking that powers `/search`.
- `analysis/explore.py`: 3 facts about the records with pandas.
- `app/records.py` gained `load_all_records()`, which combines both data files (58 records).

### Day 5 - How LLMs work and Checkpoint 1

- `docs/how_llms_work.md`: tokens, embeddings, attention, training vs inference, context window and hallucination in my own words, with a diagram, and how that leads to RAG for CaneMitra.
- `docs/user_questions.md`: 10 real user questions and whether the data can answer them (Q6, fertiliser dose, cannot be answered from the data).
- Checkpoint 1: the API running with `/docs` (`docs/checkpoint1_docs.png`) and an explanation of `ask()` in `app/main.py`. Tag `checkpoint-1`.

### Day 6 - LLM wrapper, `/chat` and prompts

- `app/llm.py`: one `generate()` function for Gemini or Groq, with timeout and error handling. Keys come from `.env` (not committed); `.env.example` is committed.
- `app/chat.py` and `POST /chat`: finds the best records, asks the LLM to answer only from them, returns JSON with `answer`, `confidence`, `follow_up` and `sources`.
- `prompts/`: system prompt (v1 and v2) and 2 task prompts.
- `eval/prompt_compare.md`: v1 vs v2 on the 10 user questions.

### Day 7 - Chunking, embeddings and semantic search

- `app/chunking.py`: splits `data/raw/` documents into overlapping word chunks that keep source, page and title; output `data/chunks.json`.
- `app/embed.py` and `app/vectorstore.py`: `all-MiniLM-L6-v2` embeddings (local, no key) stored in a persistent Chroma collection in `data/chroma/` (not committed; rebuild with `python -m app.vectorstore`).
- `GET /search/semantic?q=`: the closest chunks with scores. Top hits for the 10 questions are in `eval/search_results.md`.

### Day 8 - RAG with citations and evaluation

- `app/rag.py` and `POST /ask`: retrieves the top-k chunks, asks the LLM to answer only from them, checks that every citation is a retrieved chunk, and answers "I don't know" without calling the LLM when the best score is below `RAG_MIN_SCORE` (default 0.25).
- `eval/eval_set.json` (15 questions, 3 that must get "I don't know") and `eval/run_eval.py` compare two configs; results are in `eval/results.md` and the table below.

<!-- EVAL:START -->
| Config | Chunk size | Top-k | Chunks | Retrieval hit | Answer correct | Correct "I don't know" | With citations | Overall | Avg sec/question |
|---|---|---|---|---|---|---|---|---|---|
| A | 120 words | 3 | 139 | 6/12 (50%) | 4/12 (33%) | 3/3 (100%) | 5/12 (42%) | 7/15 (47%) | 5.35 |
| **B (winner)** | 250 words | 5 | 64 | 9/12 (75%) | 6/12 (50%) | 3/3 (100%) | 7/12 (58%) | 9/15 (60%) | 14.77 |
<!-- EVAL:END -->

### Day 9 - Agent with tools

- `app/tools.py`: `cane_harvest_window(variety, season, planting_date)` adds the crop duration from the records to the planting date and returns the earliest and latest harvest month (for example Co 419, suru, 2026-12-15: December 2027 to February 2028). `run_tool()` never raises; it returns `{"error": ...}`.
- `app/agent_loop.py`: hand-written agent loop (the LLM replies with JSON: call a tool or give a final answer; at most 5 steps).
- `app/graph.py` and `POST /agent`: the same agent in LangGraph with memory per `thread_id` and one approval step before `cane_harvest_window` runs (`awaiting_approval`, then send `approve: true` or `false`). Memory is in RAM and is lost when the server restarts.

### Day 10 - Streamlit UI and season timeline (Checkpoint 2)

- `ui/app.py`: Streamlit chat that calls `/ask` or `/agent` (chosen in the sidebar), shows the answer, confidence and **citations**, and has 👍 / 👎 buttons.
- `ui/feedback.py`: saves every thumbs click as one JSON line in `data/feedback.jsonl`.
- `ui/timeline.py`: the **season timeline bar**. Pick adsali, preseasonal or suru and a planting date; it draws planting, fertiliser split dates and the harvest window month by month.
- Friendly errors when the API is down or slow.
- Screenshot: `docs/day10_ui.png`. Tag: `checkpoint-2`.

### Day 11 - Tests, lint and Docker

- `tests/`: **42 pytest tests** for records, smart search, the harvest-window tool, `/health`, `/records`, `/search`, `/questions`, `/ask` and `/agent` (including the approval step). A fake LLM and a fake Chroma index replace the real ones, so the tests need no key, no network and no model download.
- `ruff.toml`: lint settings; `ruff check .` passes.
- `Dockerfile`, `.dockerignore`, `docker-compose.yml`: start the API and the UI with `docker compose up --build`. CPU-only PyTorch keeps the image small; `./data` is mounted so the containers use your Chroma index.

## Project structure

```
.
├── README.md
├── .gitignore
├── .dockerignore
├── .env.example             # key names only; copy to .env
├── requirements.txt
├── pytest.ini
├── ruff.toml
├── Dockerfile
├── docker-compose.yml
├── day01/ ... day11/        # one README per day (day01 and day02 also hold scripts)
├── app/                     # shared package
│   ├── records.py           # load_records, load_all_records, search, count_by, get_by_id
│   ├── cli.py               # command-line menu
│   ├── models.py            # Record dataclass
│   ├── fetch.py             # download sources into data/raw/
│   ├── ingest.py            # clean raw data into data/records.json
│   ├── smart_search.py      # TF-IDF + cosine similarity search
│   ├── llm.py               # Gemini / Groq wrapper (Day 6)
│   ├── chat.py              # /chat prompt building and reply parsing (Day 6)
│   ├── chunking.py          # documents -> chunks (Day 7)
│   ├── embed.py             # embedding model (Day 7)
│   ├── vectorstore.py       # Chroma index and semantic search (Day 7)
│   ├── rag.py               # retrieve + answer with citations (Day 8)
│   ├── tools.py             # agent tools: cane_harvest_window, rag_search (Day 9)
│   ├── agent_loop.py        # hand-written agent (Day 9)
│   ├── graph.py             # LangGraph agent with memory and approval (Day 9)
│   └── main.py              # FastAPI service with all endpoints
├── ui/                      # Streamlit front end (Day 10)
│   ├── app.py               # chat, citations, thumbs, timeline chart
│   ├── timeline.py          # planting, fertiliser splits, harvest window
│   └── feedback.py          # saves thumbs to data/feedback.jsonl
├── tests/                   # pytest tests (Day 11)
│   ├── conftest.py          # fake LLM, fake index, fake agent graph
│   ├── test_records.py
│   ├── test_tools.py
│   └── test_api.py
├── prompts/                 # system prompt v1/v2 and task prompts (Day 6)
├── eval/                    # prompt compare (Day 6), semantic eval (Day 7), RAG eval (Day 8)
├── analysis/
│   └── explore.py           # 3 facts with pandas
├── docs/                    # how_llms_work.md, user_questions.md and screenshots
└── data/
    ├── sample_records.json  # 16 hand-entered MPKV records
    ├── records.json         # 42 cleaned TNAU records (output of ingest)
    ├── chunks.json          # text chunks (output of app.chunking)
    ├── chroma/              # vector index (not committed; rebuild with python -m app.vectorstore)
    ├── feedback.jsonl       # thumbs up/down log (created by the UI, not committed)
    ├── raw/                 # downloaded source files
    └── source/
        └── mpkv_sugarcane_varieties.pdf
```

## Setup (Windows)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Put your own API key in `.env` (never commit it). Then build the vector index once:

```
python -m app.vectorstore
```

Run every command from the repository root.

## How to run

**Day 1**

```
python day01\day01_intro.py
python day01\day01_menu.py
```

**Day 2**

```
python day02\day02_s1.py
python -m app.cli
```

CLI menu: `1` list all, `2` search by keyword, `3` count per season, `4` count per institute, `5` get by id (for example `V10`), `0` exit.

**Day 3** - download the sources, then clean them:

```
python -m app.fetch
python -m app.ingest
```

**Day 4 onwards** - start the API:

```
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to try every endpoint in the browser.

| Endpoint                         | What it does                                                                                                                              |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /health`                    | Status and number of records (58)                                                                                                         |
| `GET /records?limit=5`           | First 5 records (default 10)                                                                                                              |
| `GET /records/V10`               | One record, or 404 if the id does not exist                                                                                               |
| `GET /search?q=saline soil`      | Best matching records with a TF-IDF similarity score                                                                                      |
| `POST /questions`                | Body `{"question": "..."}`; returns the closest variety, its traits and source                                                            |
| `POST /chat`                     | Day 6: LLM answer from the best records as JSON (`answer`, `confidence`, `follow_up`, `sources`). Needs a key in `.env`                   |
| `GET /search/semantic?q=...&k=3` | Day 7: closest text chunks by meaning, with source, page, title and score                                                                 |
| `POST /ask`                      | Day 8: RAG answer from retrieved chunks with verified citations, or "I don't know". Body `{"question": "...", "top_k": 5}`                 |
| `POST /agent`                    | Day 9: agent with tools and memory. `{"question": "..."}` returns `done` or `awaiting_approval`; `{"thread_id": "...", "approve": true}` continues |

Example:

```
curl -X POST http://127.0.0.1:8000/questions -H "Content-Type: application/json" -d "{\"question\": \"saline soil\"}"
```

Agent examples (`python -m app.tools` and `python -m app.agent_loop "..."` also work from the command line):

```
python -m app.tools
python -m app.agent_loop "When can I harvest Co 419 planted on 2026-12-15 in suru?"
```

Run the analysis and the evaluations:

```
python -m analysis.explore
python -m eval.semantic_eval
python eval\run_eval.py --check
```

**Day 10** - the chat UI. Start the API in one terminal, the UI in a second:

```
uvicorn app.main:app --reload
streamlit run ui/app.py
```

Open [http://localhost:8501](http://localhost:8501). In the sidebar choose `ask` or `agent`, a season and a planting date. Check the timeline logic alone with:

```
python -m ui.timeline
```

## Run tests and lint

```
python -m pytest
ruff check .
```

The 42 tests use a fake LLM and a fake index, so they need no key, no network and no model download. Run `ruff` from the repository root.

## Run with Docker

Needs Docker Desktop. Put your keys in `.env` first (copy `.env.example`), and build the index once on your PC with `python -m app.vectorstore`.

```
docker compose up --build
```

- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- UI: [http://localhost:8501](http://localhost:8501)

Stop with `Ctrl+C`, then `docker compose down`. Notes:

- The `data/` folder is shared with the containers, so they use your Chroma index and the thumbs feedback is saved on your PC.
- If `/ask` says the index is empty, build it inside Docker: `docker compose run --rm api python -m app.vectorstore`.
- The first `/ask` downloads the embedding model once; it is kept in a Docker volume.
- `.env` is passed in when the containers start and is never copied into the image.
- If the build stops with a network error, run the same command again; downloaded packages are cached.

## Data

| File                       | Records          | Source                                | Seasons                                  |
| -------------------------- | ---------------- | ------------------------------------- | ---------------------------------------- |
| `data/sample_records.json` | 16 (`V01`-`V16`) | MPKV PDF, hand-entered                | adsali, preseasonal, suru                |
| `data/records.json`        | 42 (`T01`-`T42`) | TNAU page, cleaned by `app/ingest.py` | early, mid, late, special (where listed) |
| `data/chunks.json`         | 97 chunks        | MPKV PDF (32) and TNAU page (65)      | not applicable                           |

Fields of `sample_records.json`: `id`, `variety_name`, `release_year`, `institute`, `recommended_seasons`, `cane_yield_t_ha` (per season), `duration_months` (per season), `key_traits`, `state`, `source_url`.

Fields of `records.json`: `id`, `variety_name`, `release_year` (always `null`), `recommended_seasons`, `cane_yield_t_ha` (`{"all_seasons": value}`), `key_traits` (duration, CCS %, and a short note where the page has one), `source_url`.

Fields of each chunk in `chunks.json`: `id`, `text`, `source` (file name), `page`, `title`.

Data notes:

- **V13 (Phule 09057):** the PDF gives no cane yield, so `cane_yield_t_ha` is empty.
- **V16 (Phule 13007):** one yield for all seasons, stored under `all_seasons`.
- **V14 and V15:** the PDF lists a duration of 12 months, stored as `[12, 12]`.
- **TNAU records:** the page gives no release year, so it is `null`; no value was invented. TNAU seasons are Tamil Nadu seasons and are not converted to Maharashtra's. Only some varieties appear in the page's season table, so many records have no season.
- The TNAU records are for Tamil Nadu and are not Maharashtra recommendations. Every record keeps its `source_url`.
- **Feedback:** `data/feedback.jsonl` holds one JSON object per thumbs click (`time`, `rating`, `endpoint`, `question`, `answer`, `sources`).

## Sources

| Source                                                                                                                                                                               | Used for                                     | Saved as                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------- | ------------------------------------------------------------------------- |
| MPKV sugarcane varieties PDF: [https://mpkv.ac.in/Uploads/Research/09%20-%20Sugarcane_20230830095518.pdf](https://mpkv.ac.in/Uploads/Research/09%20-%20Sugarcane_20230830095518.pdf) | 16 hand-entered Maharashtra records, chunks  | `data/raw/mpkv_sugarcane.pdf`, `data/source/mpkv_sugarcane_varieties.pdf` |
| TNAU Agritech sugarcane page: [https://agritech.tnau.ac.in/agriculture/sugarcrops_sugarcane.html](https://agritech.tnau.ac.in/agriculture/sugarcrops_sugarcane.html)                 | 42 cleaned records, chunks                   | `data/raw/tnau_sugarcane.html`                                            |

`app/fetch.py` still has a placeholder for a third source (`third_source.html`). No third document is downloaded yet.

## Limitations

- Keyword search (TF-IDF) matches words and not meaning. Short keyword queries such as `saline soil` work best. `/search/semantic` and `/ask` match by meaning.
- `POST /questions` returns the best matching records. It does not generate a written answer.
- **RAG quality:** the best config (B) answers 6 of 12 answerable questions correctly and gets all 3 unanswerable ones right with "I don't know" (see the table above). Answers can still be wrong or incomplete.
- Season rules and recommendations have not yet been verified against the full source guides and should not be presented as farmer guidance.
- **Season timeline (Day 10):** the crop durations (adsali 18, preseasonal 15, suru 12 months), the fertiliser split days (0/45/90, plus 135 for adsali and preseasonal) and the 30-day harvest window are placeholder assumptions in `ui/timeline.py`. They are not yet verified against the MPKV guide. (The agent's `cane_harvest_window` tool uses the durations from the records instead.)
- Agent memory (`MemorySaver`) is in RAM and is lost when the server restarts.
- Thumbs feedback is only logged to a local file. Nothing uses it yet to improve answers.
- The tests use a fake LLM, so they check our code and not the quality of real model answers.

## Git workflow

Each file is committed on its own with a message starting with the day, for example `D3:` or `D11:`. Check `git status` before committing and make sure `.venv` and `.env` never show up as staged. Tags: `week-1` (Days 1-4), `checkpoint-1` (Day 5) and `checkpoint-2` (Day 10). Push a tag with `git tag NAME` then `git push origin NAME`.

## Next steps

- Verify the timeline numbers and season rules against the MPKV guide, then make the UI timeline read `duration_months` from the matching variety record, like the agent tool does.
- Improve retrieval (config B still misses 3 of 12 answerable questions) and re-run `python eval\run_eval.py --write-readme`.
- Use the saved thumbs feedback to find weak answers and improve prompts.
- Add a real third source in `app/fetch.py`.