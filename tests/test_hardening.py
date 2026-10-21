"""Server hardening: setup locked behind SETUP_TOKEN, sign-in throttled per account."""

from conftest import csrf_of, hx_post


def test_setup_needs_token_when_configured(client, monkeypatch):
    monkeypatch.setenv("SETUP_TOKEN", "s3cret-setup")
    assert client.get("/setup").status_code == 403
    assert client.get("/setup?token=wrong").status_code == 403
    assert client.get("/setup?token=s3cret-setup").status_code in (200, 302)  # 302 once an owner exists
    token = csrf_of(client)
    r = hx_post(client, "/setup", {"display_name": "X", "email": "x@example.com", "password": "longenough1", "confirm": "longenough1"}, token)
    assert r.status_code == 403 and r.get_json()["title"] == "Setup is locked"


def test_sign_in_throttled_after_repeated_failures(client):
    token = csrf_of(client)
    form = {"email": "nobody@example.com", "password": "wrong-password"}
    codes = [hx_post(client, "/login", form, token).status_code for _ in range(9)]
    assert codes[:8] == [422] * 8 and codes[8] == 429
    assert hx_post(client, "/login", form, token).get_json()["title"] == "Too many attempts"


def test_security_headers(client):
    r = client.get("/login")
    assert r.headers["X-Frame-Options"] == "DENY" and r.headers["Cache-Control"] == "no-store"
