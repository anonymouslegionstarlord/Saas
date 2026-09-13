import os
import sqlite3
from contextlib import contextmanager


def database_path() -> str:
    return os.getenv("DATABASE_URL", "grantpilot.db")


@contextmanager
def connect():
    connection = sqlite3.connect(database_path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS tenants (id INTEGER PRIMARY KEY, name TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, tenant_id INTEGER NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, FOREIGN KEY(tenant_id) REFERENCES tenants(id));
        CREATE TABLE IF NOT EXISTS grants (
          id INTEGER PRIMARY KEY, tenant_id INTEGER NOT NULL, funder TEXT NOT NULL, program TEXT NOT NULL,
          deadline TEXT NOT NULL, requested_cents INTEGER NOT NULL, awarded_cents INTEGER NOT NULL DEFAULT 0,
          owner TEXT NOT NULL, status TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(tenant_id) REFERENCES tenants(id)
        );
        """)

