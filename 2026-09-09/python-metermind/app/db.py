import os,sqlite3
from contextlib import contextmanager
@contextmanager
def connect():
    db=sqlite3.connect(os.getenv('DATABASE_PATH','metermind.db'));db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
    try: yield db;db.commit()
    finally: db.close()
def init_db():
    with connect() as db: db.executescript("""
    CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS meters(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,location TEXT NOT NULL,unit TEXT NOT NULL CHECK(unit IN ('kWh','litres','m3')),alert_percent INTEGER NOT NULL CHECK(alert_percent BETWEEN 1 AND 500),UNIQUE(tenant_id,name));
    CREATE TABLE IF NOT EXISTS readings(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),meter_id INTEGER NOT NULL REFERENCES meters(id) ON DELETE CASCADE,reading_on TEXT NOT NULL,value REAL NOT NULL CHECK(value>=0),note TEXT NOT NULL DEFAULT '',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,UNIQUE(tenant_id,meter_id,reading_on));
    CREATE INDEX IF NOT EXISTS idx_readings_meter_date ON readings(tenant_id,meter_id,reading_on);
    """)

