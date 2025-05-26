import sqlite3
from contextlib import contextmanager

DATABASE_PATH = 'articles.db'

DB_NAME = "articles.db"

def get_connection():
    conn = sqlite3.connect('articles.db')
    conn.row_factory = sqlite3.Row  # allows access by column name
    return conn

@contextmanager
def transaction():
    conn = get_connection()
    try:
        conn.execute("BEGIN")
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
