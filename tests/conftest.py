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


OWNER = {"display_name": "Owner Test", "email": "owner@example.com", "password": "correct-horse-1", "confirm": "correct-horse-1"}


def login(client, email, password):
    """Sign in and return a fresh CSRF token for the new session."""
    r = hx_post(client, "/login", {"email": email, "password": password}, csrf_of(client))
    assert r.status_code == 200, r.get_data(as_text=True)
    return csrf_of(client)


def ensure_owner(client):
    """Create the platform owner if this run has none yet, then sign in as them."""
    from modules.platform.users import user_count

    if user_count() == 0:
        assert hx_post(client, "/setup", OWNER, csrf_of(client)).status_code == 200
        hx_post(client, "/login/logout", {}, csrf_of(client))
    return login(client, OWNER["email"], OWNER["password"])


def csrf_of(client):
    """Load whichever page renders in the current state so the session gets a CSRF token, then read it back."""
    for path in ("/setup", "/companies", "/login"):
        client.get(path)
    with client.session_transaction() as s:
        return s.get("csrf")
