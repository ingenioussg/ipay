"""Test set-up: a throwaway ipay_test database, rebuilt once per run.

Tests that touch the database use the `client` fixture; pure tests need nothing.
"""

import os

import pytest
from dotenv import load_dotenv

load_dotenv()
os.environ["POSTGRES_DB"] = "ipay_test"
os.environ.setdefault("FLASK_SECRET_KEY", "test-only-not-a-real-key")


@pytest.fixture(scope="session")
def app():
    from schemaconnect.postgres.migrations.migrate import drop_test_database, migrate_all

    drop_test_database()
    migrate_all()
    from routing import app as flask_app

    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


def hx_post(client, path, data, token):
    """POST as htmx would: form-encoded, with the CSRF header."""
    return client.post(path, data=data, headers={"HX-Request": "true", "X-CSRF-Token": token})


def csrf_of(client):
    """Load whichever page renders in the current state so the session gets a CSRF token, then read it back."""
    for path in ("/setup", "/companies", "/login"):
        client.get(path)
    with client.session_transaction() as s:
        return s.get("csrf")
