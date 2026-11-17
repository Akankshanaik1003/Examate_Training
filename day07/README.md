# Day 7 - Chunking, embeddings and semantic search

Date: Sat 14 Nov

Day 7 moves CaneMitra from keyword (TF-IDF) search to **semantic search**. The source documents are split into chunks that remember where they came from, every chunk is turned into an embedding, and the chunks are stored in a persistent Chroma collection that the API can search.

The code lives in the shared `app/` and `eval/` folders (like Days 3, 4 and 6). This folder only holds this README.

## Task

**S1 - chunking and embeddings**

- `app/chunking.py` + `app/embed.py`: chunk the CaneMitra documents, keeping **source, page and title** for every chunk.
- Run semantic search for the **10 user questions**.
- Record the hits in `eval/search_results.md`.

**S2 - vector store and API**

- `app/vectorstore.py` indexes all chunks into a persistent Chroma collection.
- `GET /search/semantic?q=` returns the closest chunks.

## Files

| Path                         | What it does                                                                                  |
| ---------------------------- | --------------------------------------------------------------------------------------------- |
| `app/chunking.py`            | Reads every file in `data/raw/`, splits it into overlapping word chunks, writes `data/chunks.json` |
| `app/embed.py`               | Loads the embedding model, `embed_texts()` and an in-memory `search()` used for the first test |
| `app/vectorstore.py`         | `build_index()` fills the Chroma collection in `data/chroma/`; `search()` queries it          |
| `app/main.py`                | Added `GET /search/semantic?q=`                                                               |
| `eval/questions.txt`         | The 10 user questions, one per line                                                           |
| `eval/semantic_eval.py`      | Runs the 10 questions and writes the hits to `eval/search_results.md`                         |
| `eval/search_results.md`     | Top 3 chunks per question with source, page, title, score and a relevant yes/no               |
| `data/chunks.json`           | Output of `app/chunking.py` (committed)                                                       |
| `data/chroma/`               | Persistent Chroma index (not committed, rebuild with `python -m app.vectorstore`)             |

## How it works

1. **Chunking.** PDFs are read page by page; the HTML page is one page. Text is split into chunks of 150 words with a 30 word overlap so a sentence cut at a boundary still appears whole in the next chunk. Every chunk stores `id`, `text`, `source` (file name), `page` and `title`.
2. **Embedding.** `sentence-transformers/all-MiniLM-L6-v2` turns each chunk into a 384 number vector. It runs locally, so no API key is needed. Vectors are normalised, so the dot product equals cosine similarity.
3. **Index.** `app/vectorstore.py` stores text, vector and metadata in a Chroma collection called `canemitra_chunks` (cosine distance) saved on disk.
4. **Search.** The question is embedded the same way and Chroma returns the nearest chunks. `score = 1 - distance`, so higher is better.

## How to run

Run every command from the repository root with the virtual environment active.

```
pip install -r requirements.txt
python -m app.chunking
python -m app.embed
python -m app.vectorstore
python -m eval.semantic_eval
uvicorn app.main:app --reload
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) or call:

```
curl "http://127.0.0.1:8000/search/semantic?q=which%20variety%20grows%20in%20saline%20soil&k=3"
```

Response shape:

```
{
  "query": "...",
  "results": [
    {"id": "...", "text": "...", "source": "...", "page": 1, "title": "...", "score": 0.61}
  ]
}
```

## Results

- Documents chunked: FILL (number of files)
- Chunks created: FILL (see the output of `python -m app.chunking`)
- Questions answered with a relevant chunk in the top 3: FILL / 10 (see `eval/search_results.md`)
- Example: FILL (one question where semantic search beat TF-IDF `/search`, or one where it failed)

## Notes and limitations

- Chunks keep their page number, but the TNAU HTML page has no pages, so its chunks always say page 1.
- Chunk size (150 words) and overlap (30) were chosen by hand and not tuned.
- The model is English only. Questions in Marathi or Hindi will match poorly.
- The index is built from `data/raw/`. If the raw files change, run `python -m app.chunking` and `python -m app.vectorstore` again.
- Semantic search returns chunks of source text. It does not write an answer; `POST /chat` (Day 6) still uses the TF-IDF records.