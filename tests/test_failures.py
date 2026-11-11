import logging

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app


def test_rag_failure_gives_503_without_details(client, monkeypatch, caplog):
    def broken(q):
        raise ConnectionError("vector store down: password=abc123")

    monkeypatch.setattr("app.routes.answer_question", broken)

    with caplog.at_level(logging.ERROR):
        r = client.post("/ask", json={"question": "hello"})

    assert r.status_code == 503
    assert r.json()["error"]["code"] == "rag_unavailable"
    # client ku internal detail pogakoodaadhu
    assert "abc123" not in r.text
    assert "ConnectionError" not in r.text
    assert "Traceback" not in r.text
    # aana LOG la irukkanum
    assert "abc123" in caplog.text


def test_unexpected_crash_gives_safe_500(client, app, caplog):
    def boom():
        raise RuntimeError("secret internal detail: db password=abc123")

    app.add_api_route("/test-boom", boom)

    with caplog.at_level(logging.ERROR):
        r = client.get("/test-boom")

    assert r.status_code == 500
    err = r.json()["error"]
    assert err["code"] == "internal_error"
    assert err["request_id"] == r.headers["x-request-id"]
    assert "secret" not in r.text
    assert "RuntimeError" not in r.text
    assert "Traceback" not in r.text
    # full detail log la irukku
    assert "abc123" in caplog.text


def test_missing_config_stops_startup(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)  # inga .env file illa
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()
    try:
        with pytest.raises(SystemExit):
            get_settings()
        out = capsys.readouterr().out
        assert "DATABASE_URL" in out
        assert "CONFIG ERROR" in out
    finally:
        get_settings.cache_clear()


def test_docs_off_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    get_settings.cache_clear()
    try:
        c = TestClient(create_app())
        assert c.get("/docs").status_code == 404
        assert c.get("/redoc").status_code == 404
        assert c.get("/openapi.json").status_code == 404
        assert c.get("/health").status_code == 200  # API work aaganum
    finally:
        get_settings.cache_clear()


def test_docs_on_in_development(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    get_settings.cache_clear()
    try:
        c = TestClient(create_app())
        assert c.get("/docs").status_code == 200
        assert c.get("/openapi.json").status_code == 200
    finally:
        get_settings.cache_clear()
