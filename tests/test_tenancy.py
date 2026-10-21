"""Customers, their users and access rights, and country entitlement."""

from conftest import csrf_of, ensure_owner, hx_post, login
from modules.platform.companies import companies_of
from modules.platform.customers import customers, roles_of
from modules.platform.users import users_of


def test_customer_admin_users_roles_and_rights(client, app):
    token = ensure_owner(client)
    r = hx_post(client, "/admin", {"name": "Beta Group", "sg_payroll": "on", "admin_display_name": "Beta Admin",
                                   "admin_email": "admin@beta.test", "admin_password": "beta-admin-pass"}, token)
    assert r.status_code == 200
    beta = next(c for c in customers() if c["name"] == "Beta Group")
    assert {r["name"] for r in roles_of(beta["id"])} >= {"Customer admin", "Payroll manager", "Viewer"}

    # the customer admin: no platform page; may add companies only in the customer's countries
    admin = app.test_client()
    t = login(admin, "admin@beta.test", "beta-admin-pass")
    assert admin.get("/admin").status_code == 403
    r = hx_post(admin, "/companies", {"name": "Beta MY Sdn Bhd", "my_payroll": "on"}, t)
    assert r.status_code == 422 and "countries" in r.get_json()["errors"]
    assert hx_post(admin, "/companies", {"name": "Beta Pte Ltd", "sg_payroll": "on"}, t).status_code == 200
    assert admin.get("/users").status_code == 200

    # a custom role, and a user limited to it and to one company
    r = hx_post(admin, "/users/roles", {"name": "Clerk"}, t)
    assert r.status_code == 422 and "permissions" in r.get_json()["errors"]
    assert hx_post(admin, "/users/roles", {"name": "Clerk", "permissions": ["employees.view", "bogus.code"]}, t).status_code == 200
    clerk_role = next(r for r in roles_of(beta["id"]) if r["name"] == "Clerk")
    assert clerk_role["permissions"] == ["employees.view"]
    company_id = companies_of(beta["id"])[0]["id"]
    r = hx_post(admin, "/users", {"display_name": "Clerk One", "email": "clerk@beta.test", "password": "clerk-pass-1",
                                  "role_id": clerk_role["id"], "company_ids": [company_id]}, t)
    assert r.status_code == 200

    # the clerk: can open the company dashboard, but not settings, users or company creation
    clerk = app.test_client()
    ct = login(clerk, "clerk@beta.test", "clerk-pass-1")
    assert clerk.get("/dashboard").status_code == 200
    assert clerk.get("/settings").status_code == 403
    assert clerk.get("/users").status_code == 403
    assert hx_post(clerk, "/companies", {"name": "Sneaky", "sg_payroll": "on"}, ct).status_code == 403

    # the admin cannot remove their own admin access
    me = next(u for u in users_of(beta["id"]) if u["email"] == "admin@beta.test")
    r = hx_post(admin, "/users/update", {"user_id": me["id"], "display_name": "Beta Admin", "role_id": clerk_role["id"],
                                         "is_active": "on", "all_companies": "on"}, t)
    assert r.status_code == 422 and "role_id" in r.get_json()["errors"]

    # the platform admin cannot take away a country a company uses
    r = hx_post(client, "/admin/customer", {"customer_id": beta["id"], "name": "Beta Group", "my_payroll": "on", "is_active": "on"}, token)
    assert r.status_code == 422 and "countries" in r.get_json()["errors"]

    # a disabled user is refused at sign-in
    clerk_user = next(u for u in users_of(beta["id"]) if u["email"] == "clerk@beta.test")
    assert hx_post(admin, "/users/update", {"user_id": clerk_user["id"], "display_name": "Clerk One", "role_id": clerk_role["id"],
                                            "all_companies": "on"}, t).status_code == 200
    late = app.test_client()
    r = hx_post(late, "/login", {"email": "clerk@beta.test", "password": "clerk-pass-1"}, csrf_of(late))
    assert r.status_code == 403 and r.get_json()["title"] == "Account disabled"
