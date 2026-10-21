"""Platform users: the first-run owner account, sign-in, lookup."""

from __future__ import annotations

from werkzeug.security import check_password_hash, generate_password_hash

from schemaconnect.postgres.connection.connection import cursor


def user_count() -> int:
    with cursor() as cur:
        cur.execute("SELECT count(*) AS n FROM platform.users")
        return cur.fetchone()["n"]


def create_user(display_name: str, email: str, password: str, is_owner: bool = False) -> dict:
    with cursor() as cur:
        cur.execute(
            """INSERT INTO platform.users (display_name, email, password_hash, is_owner)
               VALUES (%s, %s, %s, %s) RETURNING id, display_name, email, is_owner""",
            (display_name.strip(), email.strip().lower(), generate_password_hash(password), is_owner),
        )
        return cur.fetchone()


def authenticate(email: str, password: str) -> dict | None:
    """The user when the password matches, else None. Same answer for unknown email and wrong password."""
    with cursor() as cur:
        cur.execute(
            "SELECT id, display_name, email, is_owner, password_hash FROM platform.users WHERE email = %s",
            ((email or "").strip().lower(),),
        )
        row = cur.fetchone()
        if not row or not check_password_hash(row["password_hash"], password or ""):
            return None
        cur.execute("UPDATE platform.users SET last_login_at = now() WHERE id = %s", (row["id"],))
        row.pop("password_hash")
        return row


MAX_FAILURES = 8          # per email address
FAILURE_WINDOW = "15 minutes"


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


def get_user(user_id: int) -> dict | None:
    with cursor() as cur:
        cur.execute("SELECT id, display_name, email, is_owner FROM platform.users WHERE id = %s", (user_id,))
        return cur.fetchone()
