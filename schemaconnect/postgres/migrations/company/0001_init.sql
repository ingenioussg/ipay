-- Company schema, applied with search_path set to the company's schema.
-- registry mirrors the legacy Registry table: one row per setting key.

CREATE TABLE registry (
    reg_id     text        PRIMARY KEY,
    reg_value  text,
    updated_at timestamptz NOT NULL DEFAULT now()
);
