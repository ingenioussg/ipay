"""Companies: creation (each with its own schema), access by user, payroll countries.

Platform admins see every company. Customer users see their customer's companies:
all of them, or only those listed for them in platform.user_companies.
"""

from __future__ import annotations

from schemaconnect.postgres.connection.connection import connect, cursor
from schemaconnect.postgres.migrations.migrate import migrate_company

SELECT = """SELECT c.id, c.name, c.schema_name, c.sg_payroll, c.my_payroll, c.created_at, c.customer_id,
                   k.name AS customer_name, k.sg_payroll AS customer_sg, k.my_payroll AS customer_my
            FROM platform.companies c JOIN platform.customers k ON k.id = c.customer_id"""


def _scope(user: dict) -> tuple[str, tuple]:
    """WHERE clause limiting companies to what this user may open."""
    if user.get("is_platform_admin"):
        return "TRUE", ()
    if user.get("all_companies"):
        return "c.customer_id = %s", (user["customer_id"],)
    return ("c.customer_id = %s AND c.id IN (SELECT company_id FROM platform.user_companies WHERE user_id = %s)",
            (user["customer_id"], user["id"]))


def companies_for(user: dict) -> list[dict]:
    where, args = _scope(user)
    with cursor() as cur:
        cur.execute(f"{SELECT} WHERE {where} ORDER BY k.name, c.name", args)
        return cur.fetchall()


def company_for(user: dict, company_id) -> dict | None:
    """The company only if this user may open it."""
    try:
        company_id = int(company_id)
    except (TypeError, ValueError):
        return None
    where, args = _scope(user)
    with cursor() as cur:
        cur.execute(f"{SELECT} WHERE {where} AND c.id = %s", (*args, company_id))
        return cur.fetchone()


def companies_of(customer_id: int) -> list[dict]:
    with cursor() as cur:
        cur.execute(f"{SELECT} WHERE c.customer_id = %s ORDER BY c.name", (customer_id,))
        return cur.fetchall()


def create_company(customer_id: int, name: str, sg: bool, my: bool) -> dict:
    """Insert the company, then create and migrate its schema. One transaction."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO platform.companies (customer_id, name, sg_payroll, my_payroll) VALUES (%s, %s, %s, %s) RETURNING id",
            (customer_id, name.strip(), sg, my),
        )
        company_id = cur.fetchone()[0]
        schema_name = f"co_{company_id:06d}"
        cur.execute("UPDATE platform.companies SET schema_name = %s WHERE id = %s", (schema_name, company_id))
        migrate_company(cur, schema_name)
    return {"id": company_id, "schema_name": schema_name}


def update_company(company_id: int, name: str, sg: bool, my: bool) -> None:
    with cursor() as cur:
        cur.execute(
            "UPDATE platform.companies SET name = %s, sg_payroll = %s, my_payroll = %s WHERE id = %s",
            (name.strip(), sg, my, company_id),
        )
