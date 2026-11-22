# Day 12 - CI and deployment

**Date:** Fri 20 Nov
**S1:** `.github/workflows/ci.yml` (ruff, pytest, docker build); green badge in the README; 1 pull request from a feature branch merged after CI is green.
**S2:** Deploy CaneMitra on Render; live URL in the README and in the tracker; `/health` works publicly.

**Live API:** https://canemitra.onrender.com ([`/health`](https://canemitra.onrender.com/health), [`/docs`](https://canemitra.onrender.com/docs))

## Files

| Path                         | What it does                                                                                           |
| ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| `.github/workflows/ci.yml`   | CI: `lint` (ruff), `test` (pytest) and `docker` (image build, after the other two pass)                |
| `Dockerfile.render`          | Slim Docker image for Render: no PyTorch, ONNX embeddings, Chroma index built during the image build   |
| `requirements-render.txt`    | The 12 packages the API needs (versions copied from `requirements.txt`)                                |
| `app/embed.py`               | New `EMBED_BACKEND=onnx` option: same MiniLM model through ONNX Runtime instead of PyTorch             |
| `tests/test_embed.py`        | Test for the ONNX backend (no model download needed)                                                   |
| `README.md`                  | CI badge, live API link, Day 12 row and section, CI and deployment section                             |
| `day12/README.md`            | This file                                                                                              |

## Why the image is different on Render

Render's free plan gives the service **512 MB of RAM**. The normal setup loads PyTorch and sentence-transformers and uses about **880 MB** after the app starts, so it would be killed with "Out of memory". With `EMBED_BACKEND=onnx` the same `all-MiniLM-L6-v2` model runs through ONNX Runtime, PyTorch is never loaded, and the API uses about **260 MB** (measured with `/health` and the real code). Your local setup, Docker compose and the tests are not changed: without the variable, the code uses sentence-transformers as before.

## Step by step

Use PowerShell in the repository root (`E:\Examate_Training_November\Daily_task\Examate_Training`) with `(.venv)` active.

### Step 1 - New feature branch

```
git checkout main
git pull
git checkout -b render-deploy
```

### Step 2 - Add and change the files

1. Replace `app\embed.py` with the new version.
2. Create `Dockerfile.render` and `requirements-render.txt` in the repo root (next to `Dockerfile`).
3. Create `tests\test_embed.py`.
4. Replace `README.md` (root) and `day12\README.md`.
5. Delete the old Hugging Face files (Docker Spaces are paid, so they are not used):
   ```
   git rm -r deploy
   ```

### Step 3 - Check locally

```
ruff check .
python -m pytest -q
```

You want `All checks passed!` and `24 passed`.

### Step 4 - Commit and push the branch

```
git commit -m "D12: remove unused Hugging Face Space files"

git add app/embed.py
git commit -m "D12: optional ONNX embedding backend for low-memory hosting"

git add tests/test_embed.py
git commit -m "D12: test the ONNX embedding backend"

git add Dockerfile.render requirements-render.txt
git commit -m "D12: slim Docker image for Render"

git push -u origin render-deploy
```

The first commit is the deletion of `deploy\` that `git rm` staged in Step 2.

### Step 5 - Create the Render account

1. Open https://render.com and click **Get Started**.
2. Choose **GitHub** to sign up and authorize Render. (The free web service does not ask for a card.)

### Step 6 - Create the web service

1. In the Render dashboard click **New +**, then **Web Service**.
2. Choose **Build and deploy from a Git repository**, then **Next**.
3. Click **Configure account** (or "Connect GitHub"), allow Render to access the repository `Examate_Training` (you can choose "Only select repositories"), then pick `Akankshanaik1003/Examate_Training` and click **Connect**.
4. Fill in the form:

| Field | Value |
| --- | --- |
| Name | `canemitra` |
| Region | Singapore (closest to India) |
| Branch | `render-deploy` (you switch it to `main` in Step 11) |
| Language | Docker |
| Instance Type | **Free** |

5. Open **Advanced** and set:

| Field | Value |
| --- | --- |
| Dockerfile Path | `./Dockerfile.render` |
| Docker Build Context Directory | `.` |
| Health Check Path | `/health` |
| Auto-Deploy | On Commit |

6. Under **Environment Variables** click **Add Environment Variable** three times. Use the same names as in your `.env`:

| Key | Value |
| --- | --- |
| `LLM_PROVIDER` | `gemini` |
| `GEMINI_API_KEY` | your key |
| `GEMINI_MODEL` | `gemini-2.5-flash` |

7. Click **Deploy Web Service** (or **Create Web Service**).

### Step 7 - Wait for the build

Render opens the **Logs**. The first build takes about 5 to 10 minutes: it installs the packages, downloads the small ONNX embedding model and builds the Chroma index (you should see a line like `Indexed 97 chunks into data/chroma`). The build is done when the log shows `Your service is live`. The URL is at the top of the page, for example `https://canemitra.onrender.com`.

### Step 8 - Test the live API

In the browser, replace `YOUR-URL`:

- `https://YOUR-URL/health` must show `{"status":"ok","records":58}`. Open it in an incognito window too.
- `https://YOUR-URL/docs` opens the API page. Open **POST /ask**, click **Try it out**, enter `{"question": "Which variety tolerates saline soil?"}` and click **Execute**. You should get an answer with citations.

### Step 9 - Put the live URL in the README

In VS Code open `README.md`, press `Ctrl+H`, find `RENDER_URL` and replace it with your host **without** `https://`, for example `canemitra.onrender.com`. Click **Replace All** (3 places) and save. Click the links in the preview to check them. Also write the URL in `day12\README.md` if you want.

### Step 10 - Commit, push and pull request

```
git add README.md
git commit -m "D12: live URL, CI badge and Render deployment section"

git add day12/README.md
git commit -m "D12: day 12 README for Render"

git push
```

Create the pull request:

```
gh pr create --base main --head render-deploy --title "D12: Render deployment and ONNX embeddings" --body "Adds a low-memory ONNX embedding option, a slim Dockerfile for Render, the live URL and the CI badge."
```

No `gh`? On GitHub open the repository and click **Compare & pull request** on the yellow banner.

On the pull request page wait for the three checks (`Lint (ruff)`, `Tests (pytest)`, `Docker build`). When all three have a green check, click **Merge pull request**, then **Confirm merge**, then **Delete branch**.

### Step 11 - Point Render to `main`

After the merge the branch `render-deploy` is deleted, so Render must follow `main`:

1. Render dashboard, open the `canemitra` service, then **Settings**.
2. Find **Branch**, change it to `main`, and save. Render redeploys automatically.

Locally:

```
git checkout main
git pull
```

### Step 12 - Final check and tracker

- The CI badge at the top of the README on GitHub is green (after the run on `main` finishes).
- `https://YOUR-URL/health` still works after the redeploy.
- Paste the live URL and the pull request link in your tracker for D12.

## Checklist

- [ ] Pull request from `render-deploy` merged after the 3 checks were green
- [ ] Green CI badge at the top of the README
- [ ] Render service is live, `/health` works in an incognito window
- [ ] `/ask` on the live `/docs` page returns an answer with citations
- [ ] Live URL is in the README and in the tracker
- [ ] Render branch is set to `main`

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Render log: `Out of memory (used over 512Mi)` | Check the Environment tab has no `EMBED_BACKEND` override, and that the service uses `./Dockerfile.render`, not `Dockerfile`. |
| Build fails at `python -m app.vectorstore` | Read the line above the error. A network error while downloading the ONNX model: click **Manual Deploy**, then **Clear build cache & deploy**. |
| Build error `failed to read dockerfile` | Dockerfile Path must be `./Dockerfile.render` and the branch must contain that file (`git push` first). |
| Service starts but `/health` times out | Health Check Path must be `/health`; the first start after a sleep can take about a minute. |
| `/ask` returns 503 | `GEMINI_API_KEY` is missing or misspelled in the Environment tab. Fix it and Render restarts the service. |
| First request after a quiet time is slow | The free service sleeps after about 15 minutes. The next request wakes it. |
| CI `Lint` fails | Run `ruff check .` locally (`ruff check . --fix` fixes simple things). |
| CI `Tests` fails but passes locally | Read the log; tests must not need `.env`, `data/chroma` or the internet. |
| CI `Docker build` fails | Run `docker build -t canemitra:ci .` locally to see the same error. |