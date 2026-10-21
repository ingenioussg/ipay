-- Failed sign-ins, so repeated guessing on one account can be slowed down.
CREATE TABLE platform.login_failures (
    id    bigserial   PRIMARY KEY,
    email text        NOT NULL,
    ip    text,
    at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX login_failures_email_at ON platform.login_failures (email, at);
