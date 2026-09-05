import os,sqlite3
from contextlib import contextmanager
@contextmanager
def connect():
    db=sqlite3.connect(os.getenv("DATABASE_PATH","privacymap.db"));db.row_factory=sqlite3.Row;db.execute("PRAGMA foreign_keys=ON")
    try: yield db;db.commit()
    finally: db.close()
def init_db():
    with connect() as db: db.executescript("""
    CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS activities(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,owner TEXT NOT NULL,purpose TEXT NOT NULL,lawful_basis TEXT NOT NULL CHECK(lawful_basis IN ('consent','contract','legal_obligation','legitimate_interest')),data_subjects TEXT NOT NULL,retention_days INTEGER NOT NULL CHECK(retention_days BETWEEN 1 AND 36500),review_due TEXT NOT NULL,risk TEXT NOT NULL CHECK(risk IN ('low','medium','high')),status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('draft','active','archived')),UNIQUE(tenant_id,name));
    CREATE TABLE IF NOT EXISTS data_items(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,category TEXT NOT NULL,sensitive INTEGER NOT NULL DEFAULT 0,source TEXT NOT NULL,recipient TEXT NOT NULL DEFAULT '');
    """)

