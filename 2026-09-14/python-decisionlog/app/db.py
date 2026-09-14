import os, sqlite3
from contextlib import contextmanager

@contextmanager
def connect():
    db=sqlite3.connect(os.getenv("DATABASE_URL","decisionlog.db")); db.row_factory=sqlite3.Row; db.execute("PRAGMA foreign_keys=ON")
    try: yield db; db.commit()
    finally: db.close()
def init_db():
    with connect() as db: db.executescript("""
    CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,FOREIGN KEY(tenant_id) REFERENCES tenants(id));
    CREATE TABLE IF NOT EXISTS meetings(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL,title TEXT NOT NULL,held_on TEXT NOT NULL,facilitator TEXT NOT NULL,notes TEXT NOT NULL DEFAULT '',created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(tenant_id) REFERENCES tenants(id));
    CREATE TABLE IF NOT EXISTS decisions(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL,meeting_id INTEGER NOT NULL,summary TEXT NOT NULL,rationale TEXT NOT NULL DEFAULT '',owner TEXT NOT NULL,due_date TEXT,status TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(meeting_id) REFERENCES meetings(id),FOREIGN KEY(tenant_id) REFERENCES tenants(id));
    """)

