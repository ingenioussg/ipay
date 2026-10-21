from schemaconnect.postgres.libraries import *
from schemaconnect.postgres.configuration.configuration import dsn

# No module anywhere else may open its own database connection.


@contextmanager
def connect():
    """A connection that always commits or rolls back, and always closes."""
    conn = psycopg2.connect(**dsn())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def cursor():
    """A dict cursor inside a managed connection."""
    with connect() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
