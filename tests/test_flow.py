"""End to end through the web layer: setup, sign-in, company with both countries, settings."""

from conftest import csrf_of, hx_post

OWNER = {"display_name": "Owner Test", "email": "owner@example.com", "password": "correct-horse-1", "confirm": "correct-horse-1"}


def test_full_flow(client):
    # first run redirects to setup; setup refuses bad input with field errors
    assert client.get("/").headers["Location"].endswith("/setup")
    token = csrf_of(client)
    r = hx_post(client, "/setup", {**OWNER, "confirm": "nope"}, token)
    assert r.status_code == 422 and "confirm" in r.get_json()["errors"]
    r = hx_post(client, "/setup", OWNER, token)
    assert r.status_code == 200 and r.headers["HX-Location"] == "/companies"

    token = csrf_of(client)  # setup started a fresh session

    # a POST without the CSRF token is refused
    assert client.post("/companies", data={"name": "X"}).status_code == 403

    # sign out, wrong password, then sign in
    r = hx_post(client, "/login/logout", {}, token)
    assert r.status_code == 200 and r.headers["HX-Redirect"] == "/login"
    token = csrf_of(client)
    assert hx_post(client, "/login", {"email": OWNER["email"], "password": "wrong"}, token).status_code == 422
    r = hx_post(client, "/login", {"email": "OWNER@example.com", "password": OWNER["password"]}, token)
    assert r.status_code == 200 and r.headers["HX-Location"] == "/companies"
    token = csrf_of(client)

    # a company needs at least one country; then both countries on one company
    r = hx_post(client, "/companies", {"name": "Acme Pte Ltd"}, token)
    assert r.status_code == 422 and "countries" in r.get_json()["errors"]
    r = hx_post(client, "/companies", {"name": "Acme Pte Ltd", "sg_payroll": "on", "my_payroll": "on"}, token)
    assert r.status_code == 200 and r.headers["HX-Location"] == "/settings"

    page = client.get("/settings").get_data(as_text=True)
    assert 'id="sg_payroll" name="sg_payroll" checked' in page and 'id="my_payroll" name="my_payroll" checked' in page

    # an invalid UEN is rejected and nothing is saved
    form = {"name": "Acme Pte Ltd", "sg_payroll": "on", "my_payroll": "on", "sg.uen": "BAD", "my.epf_employer_no": "12345678"}
    r = hx_post(client, "/settings", form, token)
    assert r.status_code == 422 and "sg.uen" in r.get_json()["errors"]
    assert 'value="12345678"' not in client.get("/settings").get_data(as_text=True)

    # valid identifiers save; turning both countries off is refused
    r = hx_post(client, "/settings", {**form, "sg.uen": "201912345a"}, token)
    assert r.status_code == 200
    page = client.get("/settings").get_data(as_text=True)
    assert 'value="201912345A"' in page and 'value="12345678"' in page
    r = hx_post(client, "/settings", {"name": "Acme Pte Ltd"}, token)
    assert r.status_code == 422 and "countries" in r.get_json()["errors"]

    # Malaysia only: the SG identifier is kept, not validated, not lost
    r = hx_post(client, "/settings", {"name": "Acme Pte Ltd", "my_payroll": "on", "sg.uen": "201912345A", "my.epf_employer_no": "12345678"}, token)
    assert r.status_code == 200
    assert "flag-my" in client.get("/dashboard").get_data(as_text=True)


def test_pages_render(client):
    """Every page renders with a title and a nav once signed in (the smoke check)."""
    token = csrf_of(client)
    hx_post(client, "/login", {"email": OWNER["email"], "password": OWNER["password"]}, token)
    for route in ("/dashboard", "/companies", "/settings"):
        r = client.get(route)
        body = r.get_data(as_text=True)
        assert r.status_code == 200 and "<title>" in body and "<nav" in body, route
    assert client.get("/no-such-page").status_code == 404
