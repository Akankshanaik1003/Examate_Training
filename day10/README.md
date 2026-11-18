# Day 10 - Streamlit chat UI with a season timeline

**Date:** Wed 18 Nov
**Task:** `ui/app.py`, a Streamlit chat for CaneMitra that calls `/ask` or `/agent`, shows citations, saves thumbs up/down, and has the signature feature: a **season timeline bar**. Pick adsali, preseasonal or suru and a planting date, and it draws planting, fertiliser split dates and the harvest window month by month. Screenshot in the README. **Checkpoint 2 live demo. Tag `checkpoint-2`.**

## Files for Day 10

| Path                | What it does                                                                                                      |
| ------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `ui/__init__.py`    | Empty file so `ui` is a package                                                                                   |
| `ui/app.py`         | The Streamlit app: sidebar settings, timeline, chat, citations, thumbs buttons                                    |
| `ui/timeline.py`    | Pure Python timeline logic (no Streamlit): planting, fertiliser splits, harvest window. Run `python -m ui.timeline` |
| `ui/feedback.py`    | Saves each thumbs up/down as one JSON line in `data/feedback.jsonl`                                               |
| `day10/README.md`   | This file                                                                                                         |
| `docs/day10_ui.png` | Your screenshot of the running app (you take this one, see Step 6)                                                |
| `data/feedback.jsonl` | Created automatically on the first thumbs click (listed in `.gitignore`)                                        |

## Step by step

### Step 1 - Install

Activate the virtual environment, then:

```
pip install streamlit
pip freeze | findstr /i "streamlit requests pandas"
```

Add `streamlit` to `requirements.txt` (one line: `streamlit`). `requests` and `pandas` are already there from earlier days. The chart uses Altair, which comes with Streamlit.

### Step 2 - Create the files

Create the folder `ui/` in the repository root and copy in `__init__.py`, `app.py`, `timeline.py` and `feedback.py`. Create `day10/` and put this README in it.

### Step 3 - Check the timeline logic alone

```
python -m ui.timeline
```

You should see, for each season, the planting date, the fertiliser split dates, the harvest window and the harvest months. If this works, the chart part will work.

### Step 4 - Start the API and the UI (two terminals)

Terminal 1 (repository root):

```
uvicorn app.main:app --reload
```

Terminal 2 (repository root, same virtual environment):

```
streamlit run ui/app.py
```

The browser opens at http://localhost:8501.

### Step 5 - Try everything

1. In the sidebar choose **ask** (or **agent**).
2. Pick a season (adsali, preseasonal, suru) and a planting date. The timeline bar at the top redraws: green = planting, yellow = fertiliser splits, light green = crop growth, orange = harvest window.
3. Type a question, for example `Which variety is good for saline soil?`.
4. Open **Citations** under the answer. Click 👍 or 👎. The row is saved to `data/feedback.jsonl`.
5. Stop the API and ask again. You should see a friendly message, not a crash.

If your `/ask` or `/agent` endpoint expects a different request field than `question`, change `QUESTION_FIELD` at the top of `ui/app.py`. If it returns the answer under a different key, the app also tries `response` and `reply`, and citations under `sources` or `citations`.

### Step 6 - Screenshot for the README

With the timeline and one answer with citations visible, take a screenshot and save it as `docs/day10_ui.png`. The main README already links to this path.

### Step 7 - Commit, one file per commit

Check `git status` first and make sure `.venv` is not staged.

```
git add ui/__init__.py
git commit -m "D10: add ui package"
git add ui/timeline.py
git commit -m "D10: season timeline logic"
git add ui/feedback.py
git commit -m "D10: save thumbs feedback to jsonl"
git add ui/app.py
git commit -m "D10: Streamlit chat UI with citations and timeline"
git add requirements.txt .gitignore
git commit -m "D10: add streamlit to requirements"
git add docs/day10_ui.png
git commit -m "D10: UI screenshot"
git add day10/README.md
git commit -m "D10: day 10 README"
git add README.md
git commit -m "D10: update main README through day 10"
git push
```

### Step 8 - Tag Checkpoint 2

```
git tag checkpoint-2
git push origin checkpoint-2
```

### Step 9 - Live demo script (Checkpoint 2)

1. Show the timeline: pick **adsali**, then **suru**, and point out how the harvest window moves.
2. Ask a sugarcane question and open the citations.
3. Click 👍, then show the new line in `data/feedback.jsonl`.
4. Switch to **agent** and ask a question that needs a tool (if your `/agent` shows steps, open **Agent steps**).
5. Say the limitation: the timeline numbers are placeholders until verified against the MPKV guide.

## How the timeline works

| Season      | Default duration | Fertiliser splits (days after planting) |
| ----------- | ---------------- | --------------------------------------- |
| adsali      | 18 months        | 0, 45, 90, 135                          |
| preseasonal | 15 months        | 0, 45, 90, 135                          |
| suru        | 12 months        | 0, 45, 90                               |

Harvest window = planting date + duration, minus 30 days to plus 30 days. The month list is every calendar month that window touches.

**These numbers are placeholder assumptions and are not yet verified against the MPKV guide.** Before this is shown as advice, check them and edit `DEFAULT_DURATION_MONTHS` and `FERTILISER_SPLIT_DAYS` in `ui/timeline.py`. Do not present the timeline as farmer guidance until then.

## Troubleshooting

| Problem                                      | Fix                                                                                       |
| -------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `Cannot reach the API`                       | Start the API in terminal 1, check the **API URL** in the sidebar                         |
| `ModuleNotFoundError: ui`                    | Run `streamlit run ui/app.py` from the repository root, and make sure `ui/__init__.py` exists |
| API error 422                                | Your endpoint expects another field name. Change `QUESTION_FIELD` in `ui/app.py`          |
| Answer shows the whole JSON                  | Your endpoint uses another key for the answer. Add it to `call_api` in `ui/app.py`        |
| Chart is empty                               | Run `python -m ui.timeline` to check the dates, then upgrade: `pip install -U streamlit`  |
