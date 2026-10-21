"""Company settings, stored like the legacy Registry: one row per key in the company's schema."""

from __future__ import annotations

from psycopg2 import sql

from schemaconnect.postgres.connection.connection import cursor


def _table(schema_name: str):
    return sql.SQL("{}.registry").format(sql.Identifier(schema_name))


def read(schema_name: str, prefix: str = "") -> dict:
    with cursor() as cur:
        cur.execute(
            sql.SQL("SELECT reg_id, reg_value FROM {} WHERE reg_id LIKE %s").format(_table(schema_name)),
            (prefix + "%",),
        )
        return {r["reg_id"]: r["reg_value"] for r in cur.fetchall()}


def write(schema_name: str, values: dict) -> None:
    """Upsert only the given keys, so a stale screen cannot roll back other settings (legacy D15-06)."""
    if not values:
        return
    with cursor() as cur:
        for key, value in values.items():
            cur.execute(
                sql.SQL(
                    """INSERT INTO {} (reg_id, reg_value) VALUES (%s, %s)
                       ON CONFLICT (reg_id) DO UPDATE SET reg_value = EXCLUDED.reg_value, updated_at = now()"""
                ).format(_table(schema_name)),
                (key, value),
            )
