import os,sqlite3
from contextlib import contextmanager
@contextmanager
def connect():
    db=sqlite3.connect(os.getenv("DATABASE_PATH","accessaudit.db"));db.row_factory=sqlite3.Row;db.execute("PRAGMA foreign_keys=ON")
    try: yield db;db.commit()
    finally: db.close()
def init_db():
    with connect() as db: db.executescript("""
    CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS systems(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,owner TEXT NOT NULL,risk TEXT NOT NULL CHECK(risk IN ('low','medium','high')),UNIQUE(tenant_id,name));
    CREATE TABLE IF NOT EXISTS grants(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),system_id INTEGER NOT NULL REFERENCES systems(id) ON DELETE CASCADE,subject_email TEXT NOT NULL,role TEXT NOT NULL,review_due TEXT NOT NULL,decision TEXT NOT NULL DEFAULT 'pending' CHECK(decision IN ('pending','retain','revoke')),justification TEXT NOT NULL DEFAULT '',reviewed_at TEXT,UNIQUE(tenant_id,system_id,subject_email,role));
    """)

