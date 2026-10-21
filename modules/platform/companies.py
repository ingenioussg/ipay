"""Companies: creation (with their own schema), access, payroll countries."""

from __future__ import annotations

from schemaconnect.postgres.connection.connection import connect, cursor
from schemaconnect.postgres.migrations.migrate import migrate_company

COLUMNS = "c.id, c.name, c.schema_name, c.sg_payroll, c.my_payroll, c.created_at"


def companies_for(user_id: int) -> list[dict]:
    with cursor() as cur:
        cur.execute(
            f"""SELECT {COLUMNS}, cu.role FROM platform.companies c
                JOIN platform.company_users cu ON cu.company_id = c.id
                WHERE cu.user_id = %s ORDER BY c.name""",
            (user_id,),
        )
        return cur.fetchall()


def company_for(user_id: int, company_id) -> dict | None:
    """The company only if this user may open it."""
    try:
        company_id = int(company_id)
    except (TypeError, ValueError):
        return None
    with cursor() as cur:
        cur.execute(
            f"""SELECT {COLUMNS}, cu.role FROM platform.companies c
                JOIN platform.company_users cu ON cu.company_id = c.id
                WHERE cu.user_id = %s AND c.id = %s""",
            (user_id, company_id),
        )
        return cur.fetchone()


def create_company(user_id: int, name: str, sg: bool, my: bool) -> dict:
    """Insert the company, create and migrate its schema, grant the creator admin. One transaction."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO platform.companies (name, sg_payroll, my_payroll) VALUES (%s, %s, %s) RETURNING id",
            (name.strip(), sg, my),
        )
        company_id = cur.fetchone()[0]
        schema_name = f"co_{company_id:06d}"
        cur.execute("UPDATE platform.companies SET schema_name = %s WHERE id = %s", (schema_name, company_id))
        cur.execute(
            "INSERT INTO platform.company_users (company_id, user_id, role) VALUES (%s, %s, 'admin')",
            (company_id, user_id),
        )
        migrate_company(cur, schema_name)
    return {"id": company_id, "schema_name": schema_name}


def update_company(company_id: int, name: str, sg: bool, my: bool) -> None:
    with cursor() as cur:
        cur.execute(
            "UPDATE platform.companies SET name = %s, sg_payroll = %s, my_payroll = %s WHERE id = %s",
            (name.strip(), sg, my, company_id),
        )
