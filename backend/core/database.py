import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from backend.core.config import settings

pool = SimpleConnectionPool(
    minconn=1,
    maxconn=20,
    dsn=settings.DATABASE_URL
)
#get db session using generators
@contextmanager
def get_db_connection():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)