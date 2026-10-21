"""Applies the SQL migrations in platform/ and company/ in file-name order.

Each applied file is recorded in platform.schema_migrations, per scope
('platform' or a company schema name), so running again is a no-op.

    python -m schemaconnect.postgres.migrations.migrate        migrate everything
"""

from schemaconnect.postgres.libraries import *
from schemaconnect.postgres.configuration.configuration import dsn
from schemaconnect.postgres.connection.connection import connect
from psycopg2 import sql

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = """CREATE TABLE IF NOT EXISTS platform.schema_migrations (
    scope text NOT NULL, version text NOT NULL,
    applied_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (scope, version))"""


def ensure_database():
    """Create the configured database if it does not exist yet (local and test use)."""
    target = dsn()["dbname"]
    conn = psycopg2.connect(**dsn("postgres"))
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target,))
            if not cur.fetchone():
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target)))
    finally:
        conn.close()


def drop_test_database():
    """Drop the configured database. Refuses unless its name ends in _test."""
    target = dsn()["dbname"]
    if not target.endswith("_test"):
        raise RuntimeError(f"Refusing to drop {target!r}: only *_test databases may be dropped.")
    conn = psycopg2.connect(**dsn("postgres"))
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(target)))
    finally:
        conn.close()


def _files(kind):
    folder = os.path.join(HERE, kind)
    return sorted(f for f in os.listdir(folder) if f.endswith(".sql"))


def _apply(cur, kind, scope):
    cur.execute("SELECT version FROM platform.schema_migrations WHERE scope = %s", (scope,))
    done = {r[0] for r in cur.fetchall()}
    applied = []
    for name in _files(kind):
        if name in done:
            continue
        with open(os.path.join(HERE, kind, name), encoding="utf-8") as fh:
            cur.execute(fh.read())
        cur.execute("INSERT INTO platform.schema_migrations (scope, version) VALUES (%s, %s)", (scope, name))
        applied.append(name)
    return applied


def migrate_platform():
    with connect() as conn, conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS platform")
        cur.execute(LEDGER)
        return _apply(cur, "platform", "platform")


def migrate_company(cur, schema_name):
    """Create (if needed) and migrate one company schema, inside the caller's transaction."""
    cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema_name)))
    cur.execute(sql.SQL("SET LOCAL search_path TO {}, public").format(sql.Identifier(schema_name)))
    applied = _apply(cur, "company", schema_name)
    cur.execute("SET LOCAL search_path TO public")
    return applied


def migrate_all():
    ensure_database()
    result = {"platform": migrate_platform()}
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM platform.companies WHERE schema_name IS NOT NULL ORDER BY id")
        for (schema_name,) in cur.fetchall():
            result[schema_name] = migrate_company(cur, schema_name)
    return result


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    for scope, files in migrate_all().items():
        print(f"{scope}: {', '.join(files) if files else 'up to date'}")
