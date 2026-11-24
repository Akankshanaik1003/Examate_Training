# CaneMitra: interview preparation

## 60-second pitch

CaneMitra is a question-answering assistant for sugarcane farmers, students and advisors. Choosing a sugarcane variety means digging through long university PDFs that are hard to search and rarely say where an answer came from. I cleaned two sources (the MPKV guide and the TNAU page) into 58 variety records and 97 text chunks, and built a FastAPI service on top of them. It does keyword search, semantic search with a Chroma vector index, and RAG answers that cite the retrieved chunks. When the documents do not cover a question, it says "I don't know" instead of guessing. On my 15-question evaluation, the best configuration scored 9/15 overall (60%), with 75% retrieval hit and 3/3 correct "I don't know" answers. I also added a LangGraph agent with a harvest-window tool and a human-approval step, a Streamlit chat with citations and a season timeline, 28 tests, GitHub Actions CI, Docker, and a live deployment on Render. For production, I added input limits, a prompt-injection filter, a response cache and latency/token logging, and I measured it: about 10.7 s for an LLM call and under 1 ms for a cache hit.

## Hardest problem: fitting the deployed API into 512 MB

**Situation.** Locally, the API worked with the sentence-transformers model on PyTorch. When I deployed to Render's free plan, the service ran out of memory. The free plan has 512 MB of RAM, and my normal setup needed about 880 MB.

**What I did.** I measured first instead of guessing: PyTorch and the model were the main cost. I switched the deployed service to the ONNX version of the same embedding model (`EMBED_BACKEND=onnx` in `app/embed.py`), built a slim image (`Dockerfile.render`, `requirements-render.txt`, no PyTorch) and built the Chroma index while the image is built, so the server does not do it at start-up. I kept the PyTorch path for local runs and added a test for the ONNX backend (`tests/test_embed.py`).

**Result.** Memory dropped to about 260 MB and the API runs on the free plan. The trade-off is that retrieval scores can differ slightly from a local PyTorch run, and I documented that in the README.

**What I learned.** Check the deployment limits early, and keep one interface (`embed.py`) so the backend can change without touching the rest of the code.

## 10 likely questions and answers

**1. What is RAG and why did you use it instead of just asking the LLM?**
RAG means retrieving relevant text first and giving only that text to the LLM to answer from. A plain LLM can invent variety names or yields. With RAG, the answer comes from the MPKV and TNAU documents and can cite where it came from, which is what a farmer or advisor needs.

**2. How do you stop the model from hallucinating?**
Three layers. First, if the best retrieval score is below a threshold (`RAG_MIN_SCORE`, default 0.25), the API answers "I don't know" without calling the LLM. Second, the prompt tells the model to answer only from the retrieved text. Third, the code checks that every citation points to a chunk that was actually retrieved. On my evaluation it got all 3 out-of-scope questions right. It is not perfect: answers can still be wrong or incomplete.

**3. How did you evaluate it?**
I wrote a 15-question set, 12 answerable and 3 that must get "I don't know", and compared two configurations. Config A (120-word chunks, top-3) scored 7/15 (47%). Config B (250-word chunks, top-5) scored 9/15 (60%), with 9/12 retrieval hits and 6/12 correct answers. I chose B. The set is small, so I treat the results as a direction and not as a precise accuracy figure.

**4. Why did bigger chunks and a higher top-k work better?**
The 120-word chunks often split a variety's traits across pieces, so the right fact was not retrieved together. 250-word chunks keep more context in one piece, and top-5 gives the model more chances to contain the answer. The cost is slower answers: 14.77 s per question vs 5.35 s in my evaluation.

**5. Why ONNX on Render?**
The free plan has 512 MB of RAM and the PyTorch setup needed about 880 MB. The ONNX version of the same embedding model needs about 260 MB. See the story above.

**6. What does the agent do, and why the approval step?**
It is a LangGraph agent that can call a harvest-window tool (adds the crop duration from the records to the planting date) or answer from RAG. It keeps memory per `thread_id`. Before the tool runs, it pauses with `awaiting_approval` and continues only after `approve: true`. I added that to show a human-in-the-loop pattern for tools that act on user input. The memory is in RAM, so it is lost on restart.

**7. How do you protect against prompt injection?**
At the edge, `app/guard.py` rejects questions over 500 characters or containing known injection phrases, with HTTP 400 before any search or LLM call. A live test (`eval/injection_test.py`) and 5 unit tests check it. The limit is honest: it is keyword based and can be bypassed by rewording. The second layer is the grounded prompt that answers only from retrieved text. `/agent` does not have the guard yet.

**8. Tell me about your cache and its trade-offs.**
The cache keys on endpoint, question, `top_k` and prompt version, and keeps answers for 1 hour in memory. In my 13-request test, 3 repeated questions were cache hits (23.1%), answered in under 1 ms against about 10.7 s for an LLM call. The trade-offs: it is lost on restart, it only helps exact repeats, and stale answers are possible for up to an hour. It is switched off during tests so they stay independent.

**9. How do you test code that depends on an LLM?**
The 28 pytest tests use a fake LLM and a fake Chroma index, so they need no API key, no network and no model download, and they run in under a second. They check my code (routes, guard, agent loop, approval step), not the quality of real model answers. Quality is measured separately by the evaluation set. CI runs ruff, pytest and a Docker build on every push and pull request.

**10. What would you improve next?**
In this order: (1) improve retrieval, since config B still misses 3 of 12 answerable questions; (2) read real token counts from the provider instead of estimating at about 4 characters per token; (3) apply the guard and a cache to `/agent`; (4) verify the season timeline numbers, which are placeholder assumptions, against the MPKV guide; (5) use the saved thumbs feedback to find weak answers and improve prompts.

## Numbers to remember

| Item | Value |
|---|---|
| Variety records | 58 (16 MPKV + 42 TNAU) |
| Chunks (config B) | 64 chunks of 250 words (97 in the full chunk file) |
| RAG evaluation, config B | 9/15 overall (60%), retrieval 9/12, 3/3 "I don't know" |
| Tests | 28 passing, ruff clean |
| LLM call latency | about 10.7 s average (10683.9 ms) |
| Cache hit latency | under 1 ms |
| Cache hit rate (13 requests) | 23.1% |
| Tokens per request | about 251 (estimated) |
| Render memory | about 880 MB (PyTorch) down to about 260 MB (ONNX), limit 512 MB |