import os,sqlite3
from contextlib import contextmanager
@contextmanager
def connect():
    db=sqlite3.connect(os.getenv('DATABASE_URL','experimentlab.db'));db.row_factory=sqlite3.Row
    try:yield db;db.commit()
    finally:db.close()
def init_db():
    with connect() as db:db.executescript('''
    CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS experiments(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL,name TEXT NOT NULL,hypothesis TEXT NOT NULL,primary_metric TEXT NOT NULL,target_lift REAL NOT NULL,starts_on TEXT NOT NULL,ends_on TEXT NOT NULL,status TEXT NOT NULL,baseline REAL,observed REAL,notes TEXT NOT NULL DEFAULT '',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    ''')

