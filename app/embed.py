"""Day 7: local embeddings and an in-memory semantic search.

Two backends, same model (all-MiniLM-L6-v2):
  * default            sentence-transformers + PyTorch (what you use locally and in Docker)
  * EMBED_BACKEND=onnx ONNX Runtime without PyTorch: much less memory, used on Render's free plan
"""
import json
import os
from functools import lru_cache
from pathlib import Path

import numpy as np

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model():
    from sentence_transformers import SentenceTransformer  # imported here so the onnx backend never loads PyTorch

    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def get_onnx_model():
    from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

    return ONNXMiniLM_L6_V2()


def embed_texts(texts):
    if os.environ.get("EMBED_BACKEND", "").strip().lower() == "onnx":
        vectors = np.array(get_onnx_model()(list(texts)), dtype="float32")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.maximum(norms, 1e-12)  # normalised, like the default backend
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