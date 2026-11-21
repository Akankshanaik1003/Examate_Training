# Day 12 - CI and deployment

**Date:** Fri 20 Nov
**S1:** `.github/workflows/ci.yml` (ruff, pytest, docker build); green badge in the README; 1 pull request from a feature branch merged after CI is green.
**S2:** Deploy CaneMitra (Hugging Face Spaces); live URL in the README and in the tracker; `/health` works publicly.

## Files

| Path                          | What it does                                                                                     |
| ----------------------------- | ------------------------------------------------------------------------------------------------ |
| `.github/workflows/ci.yml`    | CI: `lint` (ruff), `test` (pytest) and `docker` (image build, after the other two pass)          |
| `deploy/space/Dockerfile`     | Docker image for the Hugging Face Space: API on port 7860, Chroma index built during the build   |
| `deploy/space/README.md`      | The Space settings (`sdk: docker`, `app_port: 7860`). It becomes the README of the Space only    |
| `deploy/space/sync.ps1`       | Copies the files the Space needs into the Space repository folder                                |
| `.dockerignore`               | Two new lines (`.github`, `deploy`) so they are not copied into the Docker image                 |
| `README.md`                   | CI badge, live API link, Day 12 row and section, CI and deployment section                       |
| `day11/README.md`             | Corrected to match the tests you pushed (23 tests, `pyproject.toml`)                             |
| `day12/README.md`             | This file                                                                                        |

## Why Hugging Face Spaces and not Render

The API loads PyTorch, sentence-transformers and Chroma. That needs more than the 512 MB of RAM of Render's free plan. A free Hugging Face Space has 16 GB RAM and 2 CPUs and runs Docker, so the same code works. The Space serves the **API** (`/health`, `/docs`, `/ask`, `/agent`). The Streamlit UI still runs on your PC and can use the live API: `$env:CANEMITRA_API_URL="https://HF_USER-canemitra.hf.space"`.

## Step by step

Run commands in PowerShell from the repository root with `(.venv)` active, unless it says otherwise.

### Step 1 - Start a feature branch

```
git checkout main
git pull
git checkout -b day12-ci-deploy
```

### Step 2 - Add the files

Create these files with the contents from the chat (folders `.github\workflows`, `deploy\space`, `day12` are new):

```
.github\workflows\ci.yml
deploy\space\Dockerfile
deploy\space\README.md
deploy\space\sync.ps1
day12\README.md
```

Replace `day11\README.md` and `README.md` with the new versions. Add two lines to the end of `.dockerignore`:

```
.github
deploy
```

### Step 3 - Check locally (CI runs the same commands)

```
ruff check .
python -m pytest -q
```

You want `All checks passed!` and `23 passed`.

### Step 4 - Create the Hugging Face Space

1. Sign up at https://huggingface.co (free).
2. Create a write token: **Settings -> Access Tokens -> Create new token -> type Write**. Copy it.
3. Go to https://huggingface.co/new-space and fill in:
   - **Space name:** `canemitra`
   - **License:** any (for example MIT)
   - **SDK:** Docker, template **Blank**
   - **Hardware:** CPU basic (free)
   - **Visibility:** Public (needed so `/health` works for everyone)
4. Click **Create Space**.

Your Space URL is `https://huggingface.co/spaces/YOUR_HF_USERNAME/canemitra`. The live API address is `https://YOUR_HF_USERNAME-canemitra.hf.space` (lowercase; `_` becomes `-`).

### Step 5 - Set the secrets (before the first build finishes)

In the Space: **Settings -> Variables and secrets**.

| Type | Name | Value |
| --- | --- | --- |
| Secret | `GEMINI_API_KEY` | your key (the same one as in your local `.env`) |
| Variable | `LLM_PROVIDER` | `gemini` |
| Variable | `GEMINI_MODEL` | `gemini-2.5-flash` |

Use the same names as in your `.env`. If you use Groq, add the Groq key name from your `.env` instead.

### Step 6 - Push the code to the Space

Clone the (empty) Space next to your project folder:

```
cd ..
git clone https://huggingface.co/spaces/YOUR_HF_USERNAME/canemitra canemitra-space
cd Examate_Training
```

When Git asks for a login: **username** = your Hugging Face username, **password** = the write token from Step 4.

Copy the files and push:

```
Set-ExecutionPolicy -Scope Process Bypass
.\deploy\space\sync.ps1 -SpaceDir ..\canemitra-space
cd ..\canemitra-space
git add .
git commit -m "Deploy CaneMitra API"
git push
cd ..\Examate_Training
```

The Space now builds. Open the Space page and watch **Logs**. The first build takes about 10 minutes (it downloads CPU PyTorch, installs the packages, downloads the embedding model and builds the Chroma index). When the status says **Running**, continue.

### Step 7 - Test the live API

In a browser (replace the name):

- `https://YOUR_HF_USERNAME-canemitra.hf.space/health` must show `{"status":"ok","records":58}`.
- `https://YOUR_HF_USERNAME-canemitra.hf.space/docs` opens the API page. Try `POST /ask` with `{"question": "Which variety tolerates saline soil?"}` and check you get an answer with citations.

Or in PowerShell:

```
curl https://YOUR_HF_USERNAME-canemitra.hf.space/health
```

Open the `/health` link in a private (incognito) window too, to confirm it works without logging in.

### Step 8 - Put the live URL in the README

In VS Code open `README.md`, press `Ctrl+H` and replace `HF_USER` with your lowercase Hugging Face username (it appears once, in the **Live API** line). Do the same in `day12\README.md`. Click the link to check it.

### Step 9 - Commit and push the branch

```
git status
git add .github/workflows/ci.yml
git commit -m "D12: GitHub Actions CI (ruff, pytest, docker build)"

git add deploy/space/Dockerfile deploy/space/README.md deploy/space/sync.ps1
git commit -m "D12: Hugging Face Space deployment files"

git add .dockerignore
git commit -m "D12: keep .github and deploy out of the Docker image"

git add day11/README.md
git commit -m "D12: correct day 11 README to match the tests"

git add day12/README.md
git commit -m "D12: day 12 README"

git add README.md
git commit -m "D12: CI badge, live URL and deployment section"

git push -u origin day12-ci-deploy
```

### Step 10 - Open the pull request and wait for CI

```
gh pr create --base main --head day12-ci-deploy --title "D12: CI and deployment" --body "Adds GitHub Actions CI (ruff, pytest, docker build), the Hugging Face Space deployment files, the live URL and the CI badge."
```

(No `gh`? On GitHub click **Compare & pull request** on the banner for `day12-ci-deploy`.)

On the pull request page, wait at the bottom for the checks: `Lint (ruff)`, `Tests (pytest)` and `Docker build`. The Docker job starts after the other two and can take 5 to 10 minutes. Wait until all three show a **green check**. Take a screenshot if you want proof.

If one is red: click **Details**, read the first red line, fix it on the same branch, commit and `git push`. CI runs again automatically.

### Step 11 - Merge

When all checks are green, click **Merge pull request -> Confirm merge** on GitHub (or `gh pr merge --merge --delete-branch`). Then:

```
git checkout main
git pull
git branch -d day12-ci-deploy
```

The merge starts CI again on `main`. When it is green, the badge at the top of the README turns green too. Open https://github.com/Akankshanaik1003/Examate_Training and check the badge.

### Step 12 - Tracker

Paste the live URL (`https://YOUR_HF_USERNAME-canemitra.hf.space`) and the pull request link in your tracker for D12.

## Checklist

- [ ] `.github/workflows/ci.yml` pushed, CI jobs lint, test and docker are green
- [ ] Green badge shows at the top of the README
- [ ] One pull request from `day12-ci-deploy` merged after CI was green
- [ ] Space status is Running and `/health` works in an incognito window
- [ ] `/ask` on the live `/docs` page returns an answer with citations
- [ ] Live URL is in the README and in the tracker

## Troubleshooting

| Problem | Fix |
| --- | --- |
| CI `Lint` fails | Run `ruff check .` locally and fix the lines it shows (`ruff check . --fix` fixes simple ones). |
| CI `Tests` fails but passes locally | Read the log. Tests must not need `.env`, `data/chroma` or the internet. |
| CI `Docker build` fails | Run `docker build -t canemitra:ci .` locally to see the same error. |
| Space build error: `Dockerfile not found` | `sync.ps1` was not run, or files were copied into a subfolder. The Space repo root must contain `Dockerfile`, `README.md`, `app/`, `data/`, `prompts/`. |
| Space build error in `python -m app.vectorstore` | Check that `data/chunks.json` is in the Space repo (`sync.ps1` copies it). |
| Space shows "Runtime error" or "Building" for a long time | Open **Logs**. A network error during `pip install` is fixed with **Settings -> Factory rebuild**. |
| `/health` works but `/ask` gives 503 | The secret is missing or misspelled. Check **Settings -> Variables and secrets**, then restart the Space. |
| `/health` is slow the first time | A free Space sleeps after a quiet period; the first request wakes it (about a minute). |
| `git push` to the Space asks for a password again | Use the write token (not your account password). |