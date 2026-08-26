import sqlite3
from contextlib import contextmanager
from datetime import date


class Store:
    def __init__(self, path: str):
        self.path = path
        self.initialize()

    @contextmanager
    def connection(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self):
        with self.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS workspaces(id INTEGER PRIMARY KEY, name TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, workspace_id INTEGER NOT NULL, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, FOREIGN KEY(workspace_id) REFERENCES workspaces(id));
                CREATE TABLE IF NOT EXISTS metrics(id INTEGER PRIMARY KEY, workspace_id INTEGER NOT NULL, name TEXT NOT NULL, unit TEXT NOT NULL, target REAL NOT NULL CHECK(target >= 0), owner TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(workspace_id) REFERENCES workspaces(id));
                CREATE TABLE IF NOT EXISTS checkins(id INTEGER PRIMARY KEY, metric_id INTEGER NOT NULL, workspace_id INTEGER NOT NULL, value REAL NOT NULL, note TEXT DEFAULT '', recorded_on TEXT NOT NULL, UNIQUE(metric_id, recorded_on), FOREIGN KEY(metric_id) REFERENCES metrics(id) ON DELETE CASCADE);
            """)

    def create_workspace_user(self, workspace: str, name: str, email: str, password_hash: str):
        with self.connection() as db:
            workspace_id = db.execute("INSERT INTO workspaces(name) VALUES(?)", (workspace,)).lastrowid
            user_id = db.execute("INSERT INTO users(workspace_id,name,email,password_hash) VALUES(?,?,?,?)", (workspace_id, name, email.lower(), password_hash)).lastrowid
            return {"id": user_id, "workspace_id": workspace_id, "name": name, "email": email.lower(), "workspace": workspace}

    def user_by_email(self, email: str):
        with self.connection() as db:
            row = db.execute("SELECT u.*, w.name workspace FROM users u JOIN workspaces w ON w.id=u.workspace_id WHERE u.email=?", (email.lower(),)).fetchone()
            return dict(row) if row else None

    def user_by_id(self, user_id: int):
        with self.connection() as db:
            row = db.execute("SELECT u.id,u.workspace_id,u.name,u.email,w.name workspace FROM users u JOIN workspaces w ON w.id=u.workspace_id WHERE u.id=?", (user_id,)).fetchone()
            return dict(row) if row else None

    def create_metric(self, workspace_id: int, name: str, unit: str, target: float, owner: str):
        with self.connection() as db:
            ident = db.execute("INSERT INTO metrics(workspace_id,name,unit,target,owner) VALUES(?,?,?,?,?)", (workspace_id, name, unit, target, owner)).lastrowid
            return self.get_metric(workspace_id, ident, db)

    def get_metric(self, workspace_id: int, metric_id: int, db=None):
        query = "SELECT m.*, (SELECT value FROM checkins c WHERE c.metric_id=m.id ORDER BY recorded_on DESC LIMIT 1) latest_value FROM metrics m WHERE m.workspace_id=? AND m.id=?"
        if db:
            row = db.execute(query, (workspace_id, metric_id)).fetchone()
            return dict(row) if row else None
        with self.connection() as conn:
            row = conn.execute(query, (workspace_id, metric_id)).fetchone()
            return dict(row) if row else None

    def list_metrics(self, workspace_id: int):
        with self.connection() as db:
            rows = db.execute("SELECT m.*, (SELECT value FROM checkins c WHERE c.metric_id=m.id ORDER BY recorded_on DESC LIMIT 1) latest_value FROM metrics m WHERE m.workspace_id=? ORDER BY m.created_at DESC", (workspace_id,)).fetchall()
            return [dict(row) for row in rows]

    def add_checkin(self, workspace_id: int, metric_id: int, value: float, note: str, recorded_on: str | None = None):
        recorded_on = recorded_on or date.today().isoformat()
        with self.connection() as db:
            if not db.execute("SELECT id FROM metrics WHERE id=? AND workspace_id=?", (metric_id, workspace_id)).fetchone():
                return None
            db.execute("INSERT INTO checkins(metric_id,workspace_id,value,note,recorded_on) VALUES(?,?,?,?,?) ON CONFLICT(metric_id,recorded_on) DO UPDATE SET value=excluded.value,note=excluded.note", (metric_id, workspace_id, value, note, recorded_on))
            return dict(db.execute("SELECT * FROM checkins WHERE metric_id=? AND recorded_on=?", (metric_id, recorded_on)).fetchone())

    def delete_metric(self, workspace_id: int, metric_id: int) -> bool:
        with self.connection() as db:
            return db.execute("DELETE FROM metrics WHERE id=? AND workspace_id=?", (metric_id, workspace_id)).rowcount == 1

