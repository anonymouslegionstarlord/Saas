import os,sqlite3
from contextlib import contextmanager
@contextmanager
def connect():
    db=sqlite3.connect(os.getenv('DATABASE_PATH','fleetledger.db'));db.row_factory=sqlite3.Row;db.execute('PRAGMA foreign_keys=ON')
    try: yield db;db.commit()
    finally: db.close()
def init_db():
    with connect() as db: db.executescript("""
    CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS vehicles(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),registration TEXT NOT NULL,label TEXT NOT NULL,fuel_type TEXT NOT NULL CHECK(fuel_type IN ('petrol','diesel','cng')),efficiency_floor REAL NOT NULL CHECK(efficiency_floor>0),UNIQUE(tenant_id,registration));
    CREATE TABLE IF NOT EXISTS fuel_logs(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL REFERENCES tenants(id),vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,filled_on TEXT NOT NULL,odometer_km REAL NOT NULL CHECK(odometer_km>=0),litres REAL NOT NULL CHECK(litres>0),cost_cents INTEGER NOT NULL CHECK(cost_cents>0),driver TEXT NOT NULL,note TEXT NOT NULL DEFAULT '',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,UNIQUE(tenant_id,vehicle_id,odometer_km));
    CREATE INDEX IF NOT EXISTS idx_fuel_logs_vehicle ON fuel_logs(tenant_id,vehicle_id,filled_on);
    """)

