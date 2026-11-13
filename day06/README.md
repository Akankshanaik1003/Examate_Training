# Day 6 - LLM provider wrapper, `/chat` endpoint and prompts

**Task (D6, Fri 13 Nov):**
- **S1:** `app/llm.py` provider wrapper (Gemini or Groq) + `POST /chat` with a CaneMitra system prompt. `.env` is NOT committed; `.env.example` is committed.
- **S2:** `prompts/` folder (system prompt + 2 task prompts). `/chat` returns JSON with `answer`, `confidence` and `follow_up`. `eval/prompt_compare.md` compares 2 prompt versions on my 10 questions.

## Where the Day 6 files are
The code is shared with other days, so it lives in `app/`, `prompts/` and `eval/`, not in this folder.

| Task part | File | Path |
|-----------|------|------|
| S1 | Provider wrapper: `generate(system, user, provider)` for Gemini and Groq, timeout and error handling | [`app/llm.py`](../app/llm.py) |
| S1 | `POST /chat` endpoint | [`app/main.py`](../app/main.py) |
| S1 | Names of the keys needed (no secrets) | [`.env.example`](../.env.example) |
| S2 | Builds the prompt from the best records, calls the LLM, parses the JSON reply | [`app/chat.py`](../app/chat.py) |
| S2 | System prompt v2 (grounded, used by default) | [`prompts/system.md`](../prompts/system.md) |
| S2 | System prompt v1 (first, looser version, kept for the comparison) | [`prompts/system_v1.md`](../prompts/system_v1.md) |
| S2 | Task prompt 1: answer from the matched records | [`prompts/task_answer.md`](../prompts/task_answer.md) |
| S2 | Task prompt 2: no record matched, so do not guess | [`prompts/task_no_match.md`](../prompts/task_no_match.md) |
| S2 | Script that runs the 10 questions through v1 and v2 | [`eval/prompt_compare.py`](../eval/prompt_compare.py) |
| S2 | The comparison result | [`eval/prompt_compare.md`](../eval/prompt_compare.md) |

## Setup
1. Copy `.env.example` to `.env` and put your own key in it (`GEMINI_API_KEY`, or `GROQ_API_KEY` and `LLM_PROVIDER=groq`).
2. `.env` is listed in `.gitignore`, so it is never committed. Check with `git status` that it is not shown.
3. No new package is needed: the wrapper uses `requests`, which is already in `requirements.txt`.

## How to run
Run from the repository root:

```
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs and try `POST /chat`, or:

```
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d "{\"question\": \"Which variety can I grow in saline soil?\"}"
```

Response:

| Field | Meaning |
|-------|---------|
| `answer` | Short answer written from the matched records only |
| `confidence` | `high` (records state it), `medium` (partly), `low` (not in the records) |
| `follow_up` | One question that would help answer better, or an empty string |
| `sources` | `source_url` of the records the answer used |

`prompt_version` (`"v1"` or `"v2"`, default `"v2"`) can be added to the request body to switch the system prompt.

Errors: an empty question gives 422; a missing key, timeout or provider error gives 503 with a short message (the key is never printed).

Run the comparison (calls the LLM 20 times):

```
python -m eval.prompt_compare
```

## How `/chat` works
1. `SmartSearch` (Day 4) finds the 3 best records for the question.
2. `app/chat.py` puts the question and those records into `prompts/task_answer.md` (or `task_no_match.md` if nothing matched).
3. `app/llm.py` sends the system prompt and the task prompt to the provider and asks for JSON.
4. The reply is parsed; if it is not valid JSON the text is returned with `confidence: low`.

## Why a second prompt version
On Day 5 I saw that search returns a close-looking record even when the data cannot answer (for example the fertilizer question Q6 scores 0.28, higher than the saline-soil question). A score threshold cannot fix this, so the rule has to be in the prompt: v2 tells the model to say "not in my records" and name the source that would have it.

## Limits
- The answer is only as good as the 3 records TF-IDF finds. If the right record is not in the top 3, the model cannot use it.
- The model can still make mistakes; every answer carries its sources so the farmer can check.
- The free tiers of Gemini and Groq have rate limits; the comparison script waits 1 second between calls.