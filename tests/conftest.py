import os
import tempfile

# IMPORTANT: app import panna MUNNADI test settings set pannanum.
# Env variables, .env file ah override pannum. So real .env touch aagaadhu.
_tmp_dir = tempfile.mkdtemp(prefix="test-db-")
os.environ["APP_ENV"] = "test"
os.environ["LLM_API_KEY"] = "test-key-not-real"
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_dir}/test.db"  # thara thatta test DB

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app as fastapi_app  # noqa: E402


@pytest.fixture
def app():
    return fastapi_app


@pytest.fixture
def client(app):
    # raise_server_exceptions=False: crash vandha test fail aagaama, 500 response ah paarkkalaam
    return TestClient(app, raise_server_exceptions=False)
