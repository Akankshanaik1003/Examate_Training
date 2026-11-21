from app.records import get_by_id, load_all_records, load_records


def test_load_records_not_empty():
    assert len(load_records()) > 0


def test_load_all_records_combines_both_files():
    # README says 58 records (16 + 42)
    assert len(load_all_records()) == 58


def test_get_by_id_found():
    rec = get_by_id(load_all_records(), "V10")
    assert rec is not None
    assert rec["id"] == "V10"


def test_get_by_id_missing_returns_none():
    assert get_by_id(load_all_records(), "DOES_NOT_EXIST") is None