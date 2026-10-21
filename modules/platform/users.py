"""Platform users: the first-run owner (platform admin), customer users, sign-in, lookup."""

from __future__ import annotations

from werkzeug.security import check_password_hash, generate_password_hash

from schemaconnect.postgres.connection.connection import cursor

# A user row with its role and customer, as the access checks expect it.
USER_SELECT = """
    SELECT u.id, u.display_name, u.email, u.is_owner, u.is_platform_admin, u.is_active, u.all_companies,
           u.customer_id, u.role_id, r.name AS role_name, r.is_admin AS role_is_admin, r.permissions,
           c.name AS customer_name, c.sg_payroll AS customer_sg, c.my_payroll AS customer_my,
           c.is_active AS customer_active
    FROM platform.users u
    LEFT JOIN platform.roles r ON r.id = u.role_id
    LEFT JOIN platform.customers c ON c.id = u.customer_id
"""

MAX_FAILURES = 8          # per email address
FAILURE_WINDOW = "15 minutes"


def user_count() -> int:
    with cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM platform.users")
        return cur.fetchone()["n"]


def create_user(display_name: str, email: str, password: str, *, is_owner: bool = False, customer_id=None,
                role_id=None, all_companies: bool = True, company_ids=(), cur=None) -> dict:
    """Owners are platform admins; everyone else belongs to a customer and has a role.
    Pass cur (a dict cursor) to join the caller's transaction."""
    if cur is None:
        with cursor() as own:
            return create_user(display_name, email, password, is_owner=is_owner, customer_id=customer_id,
                               role_id=role_id, all_companies=all_companies, company_ids=company_ids, cur=own)
    cur.execute(
        """INSERT INTO platform.users (display_name, email, password_hash, is_owner, is_platform_admin,
                                       customer_id, role_id, all_companies)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
        (display_name.strip(), email.strip().lower(), generate_password_hash(password), is_owner, is_owner,
         customer_id, role_id, all_companies),
    )
    user_id = cur.fetchone()["id"]
    _set_companies(cur, user_id, all_companies, company_ids)
    return {"id": user_id}


def _set_companies(cur, user_id, all_companies, company_ids):
    cur.execute("DELETE FROM platform.user_companies WHERE user_id = %s", (user_id,))
    if not all_companies:
        for company_id in company_ids:
            cur.execute("INSERT INTO platform.user_companies (user_id, company_id) VALUES (%s, %s)", (user_id, company_id))


def email_taken(email: str, except_user_id=None) -> bool:
    with cursor() as cur:
        cur.execute("SELECT 1 FROM platform.users WHERE email = %s AND id IS DISTINCT FROM %s",
                    ((email or "").strip().lower(), except_user_id))
        return cur.fetchone() is not None


def authenticate(email: str, password: str) -> dict | None:
    """The user when the password matches, else None. Same answer for unknown email and wrong password."""
    with cursor() as cur:
        cur.execute("SELECT id, password_hash FROM platform.users WHERE email = %s", ((email or "").strip().lower(),))
        row = cur.fetchone()
        if not row or not check_password_hash(row["password_hash"], password or ""):
            return None
        cur.execute("UPDATE platform.users SET last_login_at = now() WHERE id = %s", (row["id"],))
    return get_user(row["id"])


def is_enabled(user: dict) -> bool:
    """Active user, and (for customer users) an active customer."""
    return bool(user and user["is_active"] and (user["is_platform_admin"] or user["customer_active"]))


def get_user(user_id: int) -> dict | None:
    with cursor() as cur:
        cur.execute(USER_SELECT + " WHERE u.id = %s", (user_id,))
        return cur.fetchone()


def users_of(customer_id: int) -> list[dict]:
    with cursor() as cur:
        cur.execute(USER_SELECT + " WHERE u.customer_id = %s ORDER BY u.display_name", (customer_id,))
        users = cur.fetchall()
        cur.execute(
            """SELECT uc.user_id, uc.company_id FROM platform.user_companies uc
               JOIN platform.users u ON u.id = uc.user_id WHERE u.customer_id = %s""",
            (customer_id,),
        )
        picks = {}
        for r in cur.fetchall():
            picks.setdefault(r["user_id"], []).append(r["company_id"])
    for u in users:
        u["company_ids"] = picks.get(u["id"], [])
    return users


def update_user(customer_id: int, user_id: int, display_name: str, role_id: int, is_active: bool,
                all_companies: bool, company_ids=()) -> bool:
    """Change a customer's user. False when the user is not in that customer."""
    with cursor() as cur:
        cur.execute(
            """UPDATE platform.users SET display_name = %s, role_id = %s, is_active = %s, all_companies = %s
               WHERE id = %s AND customer_id = %s""",
            (display_name.strip(), role_id, is_active, all_companies, user_id, customer_id),
        )
        if cur.rowcount != 1:
            return False
        _set_companies(cur, user_id, all_companies, company_ids)
        return True


def too_many_failures(email: str) -> bool:
    with cursor() as cur:
        cur.execute(
            f"SELECT count(*) AS n FROM platform.login_failures WHERE email = %s AND at > now() - interval '{FAILURE_WINDOW}'",
            ((email or "").strip().lower(),),
        )
        return cur.fetchone()["n"] >= MAX_FAILURES


def record_failure(email: str, ip: str | None) -> None:
    with cursor() as cur:
        cur.execute("INSERT INTO platform.login_failures (email, ip) VALUES (%s, %s)", ((email or "").strip().lower()[:254], ip))


def clear_failures(email: str) -> None:
    with cursor() as cur:
        cur.execute("DELETE FROM platform.login_failures WHERE email = %s", ((email or "").strip().lower(),))
