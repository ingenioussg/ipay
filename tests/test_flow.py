"""End to end through the web layer: setup, sign-in, customer, company with both countries, settings."""

from conftest import OWNER, csrf_of, hx_post
from modules.platform.companies import companies_for
from modules.platform.customers import customers

ACME_ADMIN = {"admin_display_name": "Acme Admin", "admin_email": "admin@acme.test", "admin_password": "acme-admin-pass"}


def test_full_flow(client):
    # first run redirects to setup; setup refuses bad input with field errors
    assert client.get("/").headers["Location"].endswith("/setup")
    token = csrf_of(client)
    r = hx_post(client, "/setup", {**OWNER, "confirm": "nope"}, token)
    assert r.status_code == 422 and "confirm" in r.get_json()["errors"]
    r = hx_post(client, "/setup", OWNER, token)
    assert r.status_code == 200 and r.headers["HX-Location"] == "/admin"
    token = csrf_of(client)  # setup started a fresh session

    # a POST without the CSRF token is refused
    assert client.post("/companies", data={"name": "X"}).status_code == 403

    # sign out, wrong password, then sign in: the owner is platform admin and lands on /admin
    r = hx_post(client, "/login/logout", {}, token)
    assert r.status_code == 200 and r.headers["HX-Redirect"] == "/login"
    token = csrf_of(client)
    assert hx_post(client, "/login", {"email": OWNER["email"], "password": "wrong"}, token).status_code == 422
    r = hx_post(client, "/login", {"email": "OWNER@example.com", "password": OWNER["password"]}, token)
    assert r.status_code == 200 and r.headers["HX-Location"] == "/admin"
    token = csrf_of(client)

    # a customer needs a country and a fresh admin email
    r = hx_post(client, "/admin", {"name": "Acme Group", **ACME_ADMIN}, token)
    assert r.status_code == 422 and "countries" in r.get_json()["errors"]
    r = hx_post(client, "/admin", {"name": "Acme Group", "sg_payroll": "on", **ACME_ADMIN, "admin_email": OWNER["email"]}, token)
    assert r.status_code == 422 and "admin_email" in r.get_json()["errors"]
    r = hx_post(client, "/admin", {"name": "Acme Group", "sg_payroll": "on", "my_payroll": "on", **ACME_ADMIN}, token)
    assert r.status_code == 200
    acme = next(c for c in customers() if c["name"] == "Acme Group")

    # the platform admin must pick the customer for a new company; both countries on one company
    r = hx_post(client, "/companies", {"name": "Acme Pte Ltd", "sg_payroll": "on"}, token)
    assert r.status_code == 422 and "customer_id" in r.get_json()["errors"]
    r = hx_post(client, "/companies", {"customer_id": acme["id"], "name": "Acme Pte Ltd"}, token)
    assert r.status_code == 422 and "countries" in r.get_json()["errors"]
    r = hx_post(client, "/companies", {"customer_id": acme["id"], "name": "Acme Pte Ltd", "sg_payroll": "on", "my_payroll": "on"}, token)
    assert r.status_code == 200 and r.headers["HX-Location"] == "/settings"

    page = client.get("/settings").get_data(as_text=True)
    assert 'name="sg_payroll" id="sg_payroll" checked' in page and 'name="my_payroll" id="my_payroll" checked' in page

    # an invalid UEN is rejected and nothing is saved
    form = {"name": "Acme Pte Ltd", "sg_payroll": "on", "my_payroll": "on", "sg.uen": "BAD", "my.epf_employer_no": "12345678"}
    r = hx_post(client, "/settings", form, token)
    assert r.status_code == 422 and "sg.uen" in r.get_json()["errors"]
    assert 'value="12345678"' not in client.get("/settings").get_data(as_text=True)

    # valid identifiers save; turning both countries off is refused
    assert hx_post(client, "/settings", {**form, "sg.uen": "201912345a"}, token).status_code == 200
    page = client.get("/settings").get_data(as_text=True)
    assert 'value="201912345A"' in page and 'value="12345678"' in page
    r = hx_post(client, "/settings", {"name": "Acme Pte Ltd"}, token)
    assert r.status_code == 422 and "countries" in r.get_json()["errors"]

    # Malaysia only: the SG identifier is kept, not validated, not lost
    r = hx_post(client, "/settings", {"name": "Acme Pte Ltd", "my_payroll": "on", "sg.uen": "201912345A", "my.epf_employer_no": "12345678"}, token)
    assert r.status_code == 200
    assert "flag-my" in client.get("/dashboard").get_data(as_text=True)


def test_pages_render(client):
    """Every page renders with a title and a nav for the platform admin (the smoke check)."""
    hx_post(client, "/login", {"email": OWNER["email"], "password": OWNER["password"]}, csrf_of(client))
    token = csrf_of(client)
    company_id = companies_for({"is_platform_admin": True})[0]["id"]
    hx_post(client, "/companies/switch", {"company_id": company_id}, token)
    for route in ("/dashboard", "/companies", "/settings", "/admin", "/users"):
        r = client.get(route)
        body = r.get_data(as_text=True)
        assert r.status_code == 200 and "<title>" in body and "<nav" in body, route
        assert r.headers["X-Frame-Options"] == "DENY" and r.headers["Cache-Control"] == "no-store", route
    assert client.get("/no-such-page").status_code == 404
