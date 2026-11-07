"""smart_search.py - rank CaneMitra records for a query with TF-IDF + cosine similarity (Day 4, S2)."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def record_text(r: dict) -> str:
    """Everything we want a query to be able to match on, as one string."""
    return " ".join([
        r.get("variety_name", ""),
        " ".join(r.get("recommended_seasons", [])),
        r.get("key_traits", ""),
        r.get("institute", ""),
        r.get("state", ""),
    ])


class SmartSearch:
    def __init__(self, records: list[dict]):
        self.records = records
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform([record_text(r) for r in records])

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Return up to top_k records, best first, each with a 'score' (0-1). Zero-score records are dropped."""
        if not query.strip():
            return []
        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self.matrix).ravel()
        order = scores.argsort()[::-1][:top_k]
        return [{**self.records[i], "score": round(float(scores[i]), 4)} for i in order if scores[i] > 0]