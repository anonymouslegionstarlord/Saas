import os,sqlite3
from contextlib import contextmanager
@contextmanager
def connect():
    db=sqlite3.connect(os.getenv('DATABASE_URL','slaclock.db'));db.row_factory=sqlite3.Row
    try:yield db;db.commit()
    finally:db.close()
def init_db():
    with connect() as db:db.executescript('''
    CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL,subject TEXT NOT NULL,customer TEXT NOT NULL,assignee TEXT NOT NULL,priority TEXT NOT NULL,status TEXT NOT NULL,opened_at TEXT NOT NULL,due_at TEXT NOT NULL,resolved_at TEXT,description TEXT NOT NULL DEFAULT '',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    ''')

