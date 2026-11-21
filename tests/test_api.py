def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200


def test_records_limit(client):
    r = client.get("/records", params={"limit": 5})
    assert r.status_code == 200
    assert len(r.json()) == 5


def test_record_by_id(client):
    assert client.get("/records/V10").status_code == 200


def test_record_not_found(client):
    assert client.get("/records/NOPE").status_code == 404


def test_search_endpoint(client):
    r = client.get("/search", params={"q": "saline soil"})
    assert r.status_code == 200