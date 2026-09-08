import os,sqlite3
from contextlib import contextmanager
@contextmanager
def connect():
    db=sqlite3.connect(os.getenv("DATABASE_PATH","expensegate.db"));db.row_factory=sqlite3.Row;db.execute("PRAGMA foreign_keys=ON")
    try: yield db;db.commit()
    finally: db.close()
def init_db():
    with connect() as db: db.executescript("""
    CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),merchant TEXT NOT NULL,category TEXT NOT NULL,amount_cents INTEGER NOT NULL CHECK(amount_cents>0),incurred_on TEXT NOT NULL,description TEXT NOT NULL DEFAULT '',status TEXT NOT NULL DEFAULT 'submitted' CHECK(status IN ('submitted','approved','rejected')),review_note TEXT NOT NULL DEFAULT '',reviewed_at TEXT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE INDEX IF NOT EXISTS idx_expenses_tenant ON expenses(tenant_id,incurred_on);
    """)

