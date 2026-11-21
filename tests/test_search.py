from app.main import SEARCH


def test_search_returns_results():
    results = SEARCH.search("saline soil", top_k=3)
    assert len(results) > 0


def test_search_results_have_score():
    results = SEARCH.search("saline soil", top_k=3)
    assert "score" in results[0]
    assert 0 < results[0]["score"] <= 1


def test_search_respects_top_k():
    assert len(SEARCH.search("sugarcane", top_k=2)) <= 2


def test_search_empty_query_returns_empty_list():
    assert SEARCH.search("   ") == []