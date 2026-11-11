SEED_DOCS = [
    (
        "FastAPI",
        "FastAPI is a Python web framework for building APIs. It validates requests with pydantic and generates interactive docs automatically.",
    ),
    (
        "Request ID",
        "A request ID is a unique ID given to every request. It is added to every log line and error response, so one request can be traced across the logs.",
    ),
    (
        "Gitleaks",
        "Gitleaks scans code for hardcoded secrets such as API keys and passwords. As a pre-commit hook it blocks the commit when a secret is found.",
    ),
    (
        "RAG",
        "RAG means retrieval augmented generation. The system first retrieves relevant documents, then uses them to generate an answer with sources.",
    ),
    (
        "pydantic-settings",
        "pydantic-settings loads configuration from environment variables and the .env file. If a required value is missing, startup stops with a clear message.",
    ),
    (
        "Error format",
        "Every error uses one JSON shape with code, message and request_id. Stack traces stay in the logs and are never sent to clients.",
    ),
]
