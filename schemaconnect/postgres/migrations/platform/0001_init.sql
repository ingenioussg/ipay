-- Platform schema: who can sign in, which companies exist, who may open them.
-- Each company's payroll data lives in its own schema (co_000001, ...).

CREATE SCHEMA IF NOT EXISTS platform;

CREATE TABLE platform.users (
    id            bigserial PRIMARY KEY,
    email         text        NOT NULL UNIQUE CHECK (email = lower(email)),
    display_name  text        NOT NULL,
    password_hash text        NOT NULL,
    is_owner      boolean     NOT NULL DEFAULT false,
    created_at    timestamptz NOT NULL DEFAULT now(),
    last_login_at timestamptz
);

-- Exactly one owner: two first-run setups racing cannot both succeed.
CREATE UNIQUE INDEX users_one_owner ON platform.users (is_owner) WHERE is_owner;

CREATE TABLE platform.companies (
    id          bigserial PRIMARY KEY,
    name        text        NOT NULL,
    schema_name text        UNIQUE,
    sg_payroll  boolean     NOT NULL DEFAULT false,
    my_payroll  boolean     NOT NULL DEFAULT false,
    created_at  timestamptz NOT NULL DEFAULT now(),
    -- A company runs Singapore payroll, Malaysian payroll, or both; never neither.
    CONSTRAINT companies_one_country CHECK (sg_payroll OR my_payroll)
);

CREATE TABLE platform.company_users (
    company_id bigint NOT NULL REFERENCES platform.companies (id) ON DELETE CASCADE,
    user_id    bigint NOT NULL REFERENCES platform.users (id) ON DELETE CASCADE,
    role       text   NOT NULL DEFAULT 'admin',
    PRIMARY KEY (company_id, user_id)
);
