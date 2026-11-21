class FakeCollection:
    def count(self):
        return 1


def test_ask_with_fake_rag(client, monkeypatch):
    monkeypatch.setattr("app.main.get_collection", lambda: FakeCollection())
    monkeypatch.setattr(
        "app.main.answer_question",
        lambda question, top_k=3: {
            "answer": "Co 86032 is suitable.",
            "citations": ["T01"],
        },
    )
    r = client.post("/ask", json={"question": "best variety for saline soil"})
    assert r.status_code == 200
    assert "answer" in r.json()


def test_ask_empty_question_is_rejected(client):
    r = client.post("/ask", json={"question": "   "})
    assert r.status_code == 422