import os
import sqlite3
from contextlib import contextmanager


def path() -> str:
    return os.getenv("DATABASE_PATH", "vendorwatch.db")


@contextmanager
def connect():
    connection = sqlite3.connect(path())
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS tenants (id INTEGER PRIMARY KEY, name TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, tenant_id INTEGER NOT NULL REFERENCES tenants(id), name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS vendors (
          id INTEGER PRIMARY KEY, tenant_id INTEGER NOT NULL REFERENCES tenants(id), name TEXT NOT NULL,
          service TEXT NOT NULL, owner_email TEXT NOT NULL, data_access TEXT NOT NULL CHECK(data_access IN ('none','internal','confidential')),
          criticality TEXT NOT NULL CHECK(criticality IN ('low','medium','high')), status TEXT NOT NULL DEFAULT 'review' CHECK(status IN ('review','approved','restricted')),
          next_review TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(tenant_id, name)
        );
        CREATE TABLE IF NOT EXISTS assessments (
          id INTEGER PRIMARY KEY, tenant_id INTEGER NOT NULL REFERENCES tenants(id), vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
          security INTEGER NOT NULL CHECK(security BETWEEN 1 AND 5), privacy INTEGER NOT NULL CHECK(privacy BETWEEN 1 AND 5),
          resilience INTEGER NOT NULL CHECK(resilience BETWEEN 1 AND 5), comment TEXT NOT NULL DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

