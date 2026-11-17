"""Day 7: persistent Chroma index of all chunks."""
import json
from pathlib import Path

import chromadb

from app.embed import embed_texts

CHROMA_DIR = "data/chroma"
COLLECTION = "canemitra_chunks"
CHUNKS_FILE = Path("data/chunks.json")


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})


def build_index():
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    for start in range(0, len(chunks), 64):
        batch = chunks[start:start + 64]
        collection.add(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            embeddings=embed_texts([c["text"] for c in batch]).tolist(),
            metadatas=[{"source": c["source"], "page": c["page"], "title": c["title"]} for c in batch],
        )
    return collection.count()


def search(query, k=3):
    collection = get_collection()
    result = collection.query(query_embeddings=embed_texts([query]).tolist(), n_results=k)
    hits = []
    for i in range(len(result["ids"][0])):
        meta = result["metadatas"][0][i]
        hits.append({
            "id": result["ids"][0][i],
            "text": result["documents"][0][i],
            "source": meta["source"],
            "page": meta["page"],
            "title": meta["title"],
            "score": round(1 - result["distances"][0][i], 4),
        })
    return hits


if __name__ == "__main__":
    print(f"Indexed {build_index()} chunks into {CHROMA_DIR}")