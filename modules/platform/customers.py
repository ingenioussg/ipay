"""Customers (tenants) and their roles. Created by the platform admin; each starts with
the default roles and one customer admin user.
"""

from __future__ import annotations

from schemaconnect.postgres.connection.connection import cursor
from modules.platform.access import ALL, DEFAULT_ROLES
from modules.platform.users import create_user


def customers() -> list[dict]:
    with cursor() as cur:
        cur.execute(
            """SELECT c.*, (SELECT count(*) FROM platform.companies x WHERE x.customer_id = c.id) AS companies,
                      (SELECT count(*) FROM platform.users u WHERE u.customer_id = c.id) AS users
               FROM platform.customers c ORDER BY c.name"""
        )
        return cur.fetchall()


def get_customer(customer_id) -> dict | None:
    try:
        customer_id = int(customer_id)
    except (TypeError, ValueError):
        return None
    with cursor() as cur:
        cur.execute("SELECT * FROM platform.customers WHERE id = %s", (customer_id,))
        return cur.fetchone()


def create_customer(name: str, sg: bool, my: bool, admin_name: str, admin_email: str, admin_password: str) -> int:
    """Customer, its default roles and its first admin, in one transaction."""
    with cursor() as cur:
        cur.execute("INSERT INTO platform.customers (name, sg_payroll, my_payroll) VALUES (%s, %s, %s) RETURNING id",
                    (name.strip(), sg, my))
        customer_id = cur.fetchone()["id"]
        admin_role = None
        for role_name, perms, is_admin in DEFAULT_ROLES:
            cur.execute(
                "INSERT INTO platform.roles (customer_id, name, permissions, is_admin) VALUES (%s, %s, %s, %s) RETURNING id",
                (customer_id, role_name, list(perms), is_admin),
            )
            role_id = cur.fetchone()["id"]
            if is_admin:
                admin_role = role_id
        create_user(admin_name, admin_email, admin_password, customer_id=customer_id, role_id=admin_role, cur=cur)
    return customer_id


def countries_in_use(customer_id: int) -> dict:
    """Company names using each country, to stop a customer losing a country its companies run."""
    with cursor() as cur:
        cur.execute("SELECT name, sg_payroll, my_payroll FROM platform.companies WHERE customer_id = %s ORDER BY name",
                    (customer_id,))
        rows = cur.fetchall()
    return {"sg": [r["name"] for r in rows if r["sg_payroll"]], "my": [r["name"] for r in rows if r["my_payroll"]]}


def update_customer(customer_id: int, name: str, sg: bool, my: bool, is_active: bool) -> None:
    with cursor() as cur:
        cur.execute("UPDATE platform.customers SET name = %s, sg_payroll = %s, my_payroll = %s, is_active = %s WHERE id = %s",
                    (name.strip(), sg, my, is_active, customer_id))


def roles_of(customer_id: int) -> list[dict]:
    with cursor() as cur:
        cur.execute("SELECT * FROM platform.roles WHERE customer_id = %s ORDER BY is_admin DESC, name", (customer_id,))
        return cur.fetchall()


def role_of(customer_id: int, role_id) -> dict | None:
    try:
        role_id = int(role_id)
    except (TypeError, ValueError):
        return None
    with cursor() as cur:
        cur.execute("SELECT * FROM platform.roles WHERE customer_id = %s AND id = %s", (customer_id, role_id))
        return cur.fetchone()


def role_name_taken(customer_id: int, name: str, except_role_id=None) -> bool:
    with cursor() as cur:
        cur.execute("SELECT 1 FROM platform.roles WHERE customer_id = %s AND lower(name) = lower(%s) AND id IS DISTINCT FROM %s",
                    (customer_id, name.strip(), except_role_id))
        return cur.fetchone() is not None


def save_role(customer_id: int, name: str, permissions, role_id=None) -> int:
    """Create a role, or change a non-admin role. Unknown permission codes are dropped."""
    perms = sorted(set(permissions) & ALL)
    with cursor() as cur:
        if role_id is None:
            cur.execute("INSERT INTO platform.roles (customer_id, name, permissions) VALUES (%s, %s, %s) RETURNING id",
                        (customer_id, name.strip(), perms))
            return cur.fetchone()["id"]
        cur.execute("UPDATE platform.roles SET name = %s, permissions = %s WHERE id = %s AND customer_id = %s AND NOT is_admin",
                    (name.strip(), perms, role_id, customer_id))
        return role_id
