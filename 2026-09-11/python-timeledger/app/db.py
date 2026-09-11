import os,sqlite3
from contextlib import contextmanager
@contextmanager
def connect():
    db=sqlite3.connect(os.getenv('DATABASE_PATH','timeledger.db'));db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
    try: yield db;db.commit()
    finally: db.close()
def init_db():
    with connect() as db: db.executescript("""
    CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,client TEXT NOT NULL,hourly_rate_cents INTEGER NOT NULL CHECK(hourly_rate_cents>=0),budget_hours REAL NOT NULL CHECK(budget_hours>0),UNIQUE(tenant_id,name));
    CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,worked_on TEXT NOT NULL,hours REAL NOT NULL CHECK(hours>0 AND hours<=24),task TEXT NOT NULL,billable INTEGER NOT NULL CHECK(billable IN (0,1)),status TEXT NOT NULL DEFAULT 'submitted' CHECK(status IN ('submitted','approved','rejected')),review_note TEXT NOT NULL DEFAULT '',reviewed_at TEXT,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE INDEX IF NOT EXISTS idx_entries_project_date ON entries(tenant_id,project_id,worked_on);
    """)

