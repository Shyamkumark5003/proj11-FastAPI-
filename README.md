# RAG Service

A FastAPI service that wraps a small RAG core (SQLite documents + keyword retrieval).

## Setup

```bash
python3 -m venv ~/venvs/project11
source ~/venvs/project11/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env        # then fill in real values
pre-commit install          # enables the gitleaks secret scan
```

## Run

```bash
python -m uvicorn app.main:app
```

## Test

```bash
python -m pytest -v
```

Tests use a temporary SQLite database and never touch your real `.env` or `app.db`.

## Configuration

Settings come from environment variables or `.env` (see `.env.example`).
If a required value is missing, the service refuses to start and prints which one.

| Variable | Required | Description |
|---|---|---|
| `APP_ENV` | no | `development` (default), `test` or `production` |
| `LOG_LEVEL` | no | Default `INFO` |
| `DATABASE_URL` | yes | Example: `sqlite:///./app.db` |
| `LLM_API_KEY` | yes | Secret. Never logged. |

## Endpoints

- `GET /health` returns `{"status": "ok"}`
- `POST /ask` with `{"question": "..."}` returns `{"answer": "...", "sources": [...]}`

Interactive docs (`/docs`, `/redoc`, `/openapi.json`) are available only when `APP_ENV=development`.

## Errors

Every error uses one shape. Stack traces are never sent to clients; they stay in the logs.

```json
{"error": {"code": "rag_unavailable", "message": "...", "request_id": "..."}}
```

## Logging

Logs are JSON, one object per line. Every line carries a `request_id`.
The same ID is returned in the `X-Request-ID` response header and in every error body,
so one request can be traced through the logs.

## Security

`gitleaks` runs as a pre-commit hook and blocks commits that contain secrets.
