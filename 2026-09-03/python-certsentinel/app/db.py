import os,sqlite3
from contextlib import contextmanager

@contextmanager
def connect():
    db=sqlite3.connect(os.getenv("DATABASE_PATH","certsentinel.db"));db.row_factory=sqlite3.Row;db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db;db.commit()
    finally: db.close()

def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,email TEXT NOT NULL UNIQUE,password_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS people(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,email TEXT NOT NULL,department TEXT NOT NULL,UNIQUE(tenant_id,email));
        CREATE TABLE IF NOT EXISTS credentials(
          id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),person_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE,
          certification TEXT NOT NULL,issuer TEXT NOT NULL,credential_code TEXT NOT NULL DEFAULT '',issued_on TEXT NOT NULL,expires_on TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','renewing','expired','waived')),notes TEXT NOT NULL DEFAULT '',created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(tenant_id,person_id,certification)
        );
        """)

