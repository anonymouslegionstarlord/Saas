import os, sqlite3
from contextlib import contextmanager

@contextmanager
def connect():
    db = sqlite3.connect(os.getenv("DATABASE_PATH", "contractcue.db"))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
        db.commit()
    finally:
        db.close()

def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, tenant_id INTEGER NOT NULL REFERENCES tenants(id), name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS contracts(
          id INTEGER PRIMARY KEY, tenant_id INTEGER NOT NULL REFERENCES tenants(id), title TEXT NOT NULL,
          counterparty TEXT NOT NULL, owner_email TEXT NOT NULL, starts_on TEXT NOT NULL, ends_on TEXT NOT NULL,
          value_cents INTEGER NOT NULL DEFAULT 0 CHECK(value_cents>=0), status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('draft','active','expired','terminated')),
          notes TEXT NOT NULL DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(tenant_id,title)
        );
        CREATE TABLE IF NOT EXISTS obligations(
          id INTEGER PRIMARY KEY, tenant_id INTEGER NOT NULL REFERENCES tenants(id), contract_id INTEGER NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
          title TEXT NOT NULL, due_on TEXT NOT NULL, assignee TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','done','waived')),
          completed_at TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

