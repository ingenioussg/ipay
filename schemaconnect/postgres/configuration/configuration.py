from schemaconnect.postgres.libraries import *

# The only place that reads database environment variables.
# Nothing here is hardcoded: no host, port, database name, user or password.
# Read at call time, so .env loading order and test overrides cannot go stale.


def dsn(dbname=None):
    """Connection settings. Fails loudly rather than connecting as nobody."""
    password = os.getenv("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError(
            "POSTGRES_PASSWORD is not set. Copy .env.example to .env and fill it, "
            "or export the variable before starting the application."
        )
    return {
        "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "port": os.getenv("POSTGRES_PORT", "5433"),
        "dbname": dbname or os.getenv("POSTGRES_DB", "ipay"),
        "user": os.getenv("POSTGRES_USER", "ipay"),
        "password": password,
    }
