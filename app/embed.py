"""Day 7: local embeddings and an in-memory semantic search."""
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts):
    return get_model().encode(texts, normalize_embeddings=True, show_progress_bar=False)


def search(query, chunks, vectors, k=3):
    scores = vectors @ embed_texts([query])[0]
    best = np.argsort(-scores)[:k]
    return [{**chunks[i], "score": float(scores[i])} for i in best]


if __name__ == "__main__":
    data = json.loads(Path("data/chunks.json").read_text(encoding="utf-8"))
    vecs = embed_texts([c["text"] for c in data])
    for hit in search("which variety suits saline soil", data, vecs):
        print(round(hit["score"], 3), hit["source"], "p", hit["page"], "-", hit["text"][:100])