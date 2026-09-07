import os,sqlite3
from contextlib import contextmanager
@contextmanager
def connect():
    db=sqlite3.connect(os.getenv("DATABASE_PATH","findingflow.db"));db.row_factory=sqlite3.Row;db.execute("PRAGMA foreign_keys=ON")
    try: yield db;db.commit()
    finally: db.close()
def init_db():
    with connect() as db: db.executescript("""
    CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS audits(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),title TEXT NOT NULL,area TEXT NOT NULL,lead TEXT NOT NULL,starts_on TEXT NOT NULL,ends_on TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('planned','open','closed')),UNIQUE(tenant_id,title));
    CREATE TABLE IF NOT EXISTS findings(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),audit_id INTEGER NOT NULL REFERENCES audits(id) ON DELETE CASCADE,title TEXT NOT NULL,severity TEXT NOT NULL CHECK(severity IN ('low','medium','high','critical')),owner TEXT NOT NULL,due_on TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','in_progress','verified','accepted')),remediation TEXT NOT NULL DEFAULT '',verified_at TEXT);
    """)

