-- Customers (tenants) own companies and users. The platform admin (Ingenious) creates
-- customers and decides which payroll countries each may use; each customer's admin
-- manages its users and their roles.

CREATE TABLE platform.customers (
    id         bigserial   PRIMARY KEY,
    name       text        NOT NULL,
    sg_payroll boolean     NOT NULL DEFAULT false,
    my_payroll boolean     NOT NULL DEFAULT false,
    is_active  boolean     NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT customers_one_country CHECK (sg_payroll OR my_payroll)
);

CREATE TABLE platform.roles (
    id          bigserial PRIMARY KEY,
    customer_id bigint    NOT NULL REFERENCES platform.customers (id) ON DELETE CASCADE,
    name        text      NOT NULL,
    permissions text[]    NOT NULL DEFAULT '{}',
    is_admin    boolean   NOT NULL DEFAULT false,   -- the customer admin role: every permission
    UNIQUE (customer_id, name)
);

ALTER TABLE platform.users
    ADD COLUMN is_platform_admin boolean NOT NULL DEFAULT false,
    ADD COLUMN customer_id       bigint  REFERENCES platform.customers (id) ON DELETE CASCADE,
    ADD COLUMN role_id           bigint  REFERENCES platform.roles (id),
    ADD COLUMN all_companies     boolean NOT NULL DEFAULT true,
    ADD COLUMN is_active         boolean NOT NULL DEFAULT true;

ALTER TABLE platform.companies
    ADD COLUMN customer_id bigint REFERENCES platform.customers (id) ON DELETE CASCADE;

-- Existing data: the owner becomes platform admin; any companies or other users
-- move under one "Default customer" with a customer admin role.
UPDATE platform.users SET is_platform_admin = true WHERE is_owner;

DO $$
DECLARE cid bigint; rid bigint;
BEGIN
    IF EXISTS (SELECT 1 FROM platform.companies) OR EXISTS (SELECT 1 FROM platform.users WHERE NOT is_platform_admin) THEN
        INSERT INTO platform.customers (name, sg_payroll, my_payroll)
        SELECT 'Default customer', coalesce(bool_or(sg_payroll), true), coalesce(bool_or(my_payroll), false)
        FROM platform.companies
        RETURNING id INTO cid;
        INSERT INTO platform.roles (customer_id, name, is_admin) VALUES (cid, 'Customer admin', true) RETURNING id INTO rid;
        UPDATE platform.companies SET customer_id = cid WHERE customer_id IS NULL;
        UPDATE platform.users SET customer_id = cid, role_id = rid WHERE NOT is_platform_admin;
    END IF;
END $$;

ALTER TABLE platform.companies ALTER COLUMN customer_id SET NOT NULL;
ALTER TABLE platform.users ADD CONSTRAINT users_platform_or_customer CHECK (
    (is_platform_admin AND customer_id IS NULL)
    OR (NOT is_platform_admin AND customer_id IS NOT NULL AND role_id IS NOT NULL));

-- Which companies a user may open when all_companies is false.
CREATE TABLE platform.user_companies (
    user_id    bigint NOT NULL REFERENCES platform.users (id) ON DELETE CASCADE,
    company_id bigint NOT NULL REFERENCES platform.companies (id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, company_id)
);

DROP TABLE platform.company_users;
