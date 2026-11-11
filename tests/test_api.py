def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_every_response_has_request_id(client):
    r = client.get("/health")
    assert len(r.headers["x-request-id"]) == 32


def test_ask_success(client, monkeypatch):
    # RAG core ah fake pannrom, so test fast ah and stable ah irukkum
    monkeypatch.setattr(
        "app.routes.answer_question",
        lambda q: {"answer": "fake answer", "sources": ["doc1"]},
    )
    r = client.post("/ask", json={"question": "What is RAG?"})
    assert r.status_code == 200
    assert r.json() == {"answer": "fake answer", "sources": ["doc1"]}


def test_ask_empty_question_is_422(client):
    r = client.post("/ask", json={"question": ""})
    assert r.status_code == 422
    err = r.json()["error"]
    assert err["code"] == "validation_error"
    assert err["details"][0]["field"] == "body.question"


def test_ask_missing_field_is_422(client):
    r = client.post("/ask", json={})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_ask_too_long_question_is_422(client):
    r = client.post("/ask", json={"question": "a" * 2001})
    assert r.status_code == 422


def test_unknown_url_uses_error_format(client):
    r = client.get("/nothing")
    assert r.status_code == 404
    err = r.json()["error"]
    assert err["code"] == "not_found"
    # header ID and body ID rendum same
    assert err["request_id"] == r.headers["x-request-id"]
