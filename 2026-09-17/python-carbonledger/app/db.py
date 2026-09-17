import os,sqlite3
from contextlib import contextmanager
@contextmanager
def connect():
    db=sqlite3.connect(os.getenv('DATABASE_URL','carbonledger.db'));db.row_factory=sqlite3.Row
    try:yield db;db.commit()
    finally:db.close()
def init_db():
    with connect() as db:db.executescript('''
    CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL,target_kg REAL NOT NULL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS activities(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL,activity_date TEXT NOT NULL,category TEXT NOT NULL,source TEXT NOT NULL,quantity REAL NOT NULL,unit TEXT NOT NULL,factor REAL NOT NULL,kg_co2e REAL NOT NULL,notes TEXT NOT NULL DEFAULT '',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    ''')

