import os
import sqlite3

from app.config import get_settings
from app.db import init_db
from app.rag.core import ask


def make_conn():
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    return conn


def test_core_finds_relevant_doc():
    result = ask(make_conn(), "What is gitleaks?")
    assert "Gitleaks" in result["sources"]
    assert "secret" in result["answer"].lower()


def test_core_no_match():
    result = ask(make_conn(), "banana smoothie recipe")
    assert result["sources"] == []
    assert "could not find" in result["answer"].lower()


def test_ask_endpoint_uses_real_test_db(client):
    r = client.post("/ask", json={"question": "What is gitleaks?"})
    assert r.status_code == 200
    assert "Gitleaks" in r.json()["sources"]


def test_ask_endpoint_no_match_is_still_200(client):
    r = client.post("/ask", json={"question": "banana smoothie recipe"})
    assert r.status_code == 200
    assert r.json()["sources"] == []


def test_tests_use_temp_database_not_real_one(client):
    client.post("/ask", json={"question": "What is RAG?"})
    url = get_settings().database_url
    assert "test-db-" in url
    assert os.path.exists(url.removeprefix("sqlite:///"))


def test_db_down_gives_503_without_details(client, monkeypatch):
    def broken(url):
        raise sqlite3.OperationalError("unable to open database file: /secret/path/app.db")

    monkeypatch.setattr("app.rag_service.connect", broken)
    r = client.post("/ask", json={"question": "What is RAG?"})

    assert r.status_code == 503
    assert r.json()["error"]["code"] == "rag_unavailable"
    assert "secret" not in r.text
    assert "sqlite" not in r.text.lower()
