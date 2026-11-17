
"""rag.py - Day 8, S1: answer a question from retrieved chunks, with citations.

Use:
    from app.rag import answer_question
    result = answer_question("Which variety tolerates saline soil?", top_k=3)

Flow:
    1. Retrieve top-k chunks from the Chroma index.
    2. If nothing relevant is found, return "I don't know" without calling the LLM.
    3. Ask the LLM to answer ONLY from retrieved chunks.
    4. Accept citations only when they match retrieved chunk IDs.
    5. Return answer, confidence, follow_up, citations and retrieved chunks.
"""

import json
import os
import re

from app.chat import parse_reply
from app.embed import embed_texts
from app.llm import generate, load_env
from app.vectorstore import search as vector_search

load_env()

IDK = "I don't know"

# Minimum cosine similarity score.
# This is only a retrieval garbage filter, not the final answerability check.
MIN_SCORE = float(os.environ.get("RAG_MIN_SCORE", "0.25"))

SYSTEM_PROMPT = """You are CaneMitra, a friendly sugarcane assistant for farmers in Maharashtra.

You answer ONLY from the numbered context chunks given in the user message.
Never use outside knowledge.

Rules:
1. If the chunks do not clearly contain the answer, the answer must start
   with exactly: I don't know
   You may add one short sentence saying what is missing. Do not guess.

2. The documents only describe sugarcane varieties.
   If the question is about prices, markets, dealers, brands, discounts,
   news, another crop (for example wheat), or a place the chunks do not
   mention, answer: I don't know.

3. Every fact you state must come from a context chunk.
   Put the exact IDs of the chunks you used in "citations".

4. Keep the answer short and use simple words.

5. Reply with JSON only, no other text:
   {
     "answer": "...",
     "confidence": "high" or "medium" or "low",
     "follow_up": "one short question or empty",
     "citations": ["chunk id", "chunk id"]
   }

6. When the answer is "I don't know":
   - confidence must be "low"
   - citations must be []

"""


def retrieve(question: str, top_k: int = 3, collection=None) -> list[dict]:
    """Retrieve the top-k chunks for a question.

    collection=None uses the persistent Chroma index in data/chroma.
    A supplied collection is used for evaluation/testing.
    """
    if collection is None:
        return vector_search(question, top_k)

    result = collection.query(
        query_embeddings=embed_texts([question]).tolist(),
        n_results=top_k,
    )

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


def build_context(hits: list[dict]) -> str:
    """Format retrieved chunks with their IDs and source information."""
    blocks = []

    for h in hits:
        blocks.append(
            f"[{h['id']}] "
            f"(source: {h['source']}, page {h['page']}, {h['title']})\n"
            f"{h['text']}"
        )

    return "\n\n".join(blocks)


def is_idk(answer: str) -> bool:
    """Check whether the answer starts with 'I don't know'."""
    start = answer.strip().lower().replace("\u2019", "'")[:40]
    return "i don't know" in start


def _cited_ids(text: str) -> list[str]:
    """Extract citation IDs from the LLM JSON response."""
    cleaned = re.sub(
        r"^```(?:json)?|```$",
        "",
        text.strip(),
        flags=re.M,
    ).strip()

    try:
        data = json.loads(cleaned)
    except (ValueError, TypeError):
        return []

    if not isinstance(data, dict):
        return []

    items = data.get("citations", [])

    if not isinstance(items, list):
        return []

    ids = []

    for item in items:
        value = item.get("id", "") if isinstance(item, dict) else item

        if isinstance(value, str) and value.strip():
            ids.append(value.strip().strip("[] "))

    return ids


def answer_question(
    question: str,
    top_k: int = 3,
    collection=None,
    provider: str | None = None,
    min_score: float | None = None,
) -> dict:
    """Answer a question using retrieved chunks and verified citations.

    Returns:
        question
        answer
        confidence
        follow_up
        idk
        model_cited
        citations
        retrieved

    Raises:
        LLMError if the LLM call fails.
    """

    threshold = MIN_SCORE if min_score is None else min_score

    # Step 1: Retrieve relevant chunks.
    hits = retrieve(question, top_k, collection)

    # Keep retrieval details for the API response.
    retrieved = [
        {
            k: h[k]
            for k in ("id", "source", "page", "title", "score")
        }
        for h in hits
    ]

    best = hits[0]["score"] if hits else 0.0

    # Step 2: Return I don't know without calling the LLM
    # if no relevant chunks were retrieved.
    if not hits or best < threshold:
        return {
            "question": question,
            "answer": (
                f"{IDK}. "
                "I could not find this in the CaneMitra documents."
            ),
            "confidence": "low",
            "follow_up": (
                "Try asking about a sugarcane variety, season, "
                "yield, duration or soil."
            ),
            "idk": True,
            "model_cited": False,
            "citations": [],
            "retrieved": retrieved,
        }

    # Step 3: Build the context and call the LLM.
    user_message = (
        f"Question: {question}\n\n"
        f"Context chunks:\n\n"
        f"{build_context(hits)}"
    )

    raw = generate(
        SYSTEM_PROMPT,
        user_message,
        provider=provider,
    )

    # Step 4: Parse the LLM response.
    reply = parse_reply(raw)

    by_id = {
        h["id"]: h
        for h in hits
    }

    idk = is_idk(reply["answer"])
    model_cited = False
    cited = []

    if idk:
        reply["confidence"] = "low"

    else:
        # Accept only citation IDs belonging to retrieved chunks.
        cited = [
            chunk_id
            for chunk_id in _cited_ids(raw)
            if chunk_id in by_id
        ]

        # Remove duplicate citations while preserving order.
        cited = list(dict.fromkeys(cited))

        model_cited = bool(cited)

        # Do not invent citations if the model forgot to cite.
        # Return I don't know instead of an unsupported answer.
        if not cited:
            reply["answer"] = (
                f"{IDK}. "
                "I could not verify the answer with a valid chunk citation."
            )
            reply["confidence"] = "low"
            reply["follow_up"] = (
                "Could you try asking about a specific sugarcane variety?"
            )
            idk = True

    # Step 5: Build the final response.
    citations = [
        {
            k: by_id[chunk_id][k]
            for k in ("id", "source", "page", "title")
        }
        for chunk_id in cited
    ]

    return {
        "question": question,
        "answer": reply["answer"],
        "confidence": reply["confidence"],
        "follow_up": reply["follow_up"],
        "idk": idk,
        "model_cited": model_cited,
        "citations": citations,
        "retrieved": retrieved,
    }
