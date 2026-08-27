import sqlite3
from contextlib import contextmanager

class Store:
    def __init__(self, path: str):
        self.path = path
        self.setup()

    @contextmanager
    def db(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def setup(self):
        with self.db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS tenants(id INTEGER PRIMARY KEY,name TEXT NOT NULL,slug TEXT UNIQUE NOT NULL);
            CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,FOREIGN KEY(tenant_id) REFERENCES tenants(id));
            CREATE TABLE IF NOT EXISTS boards(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL,name TEXT NOT NULL,public_key TEXT UNIQUE NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(tenant_id) REFERENCES tenants(id));
            CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY,tenant_id INTEGER NOT NULL,board_id INTEGER NOT NULL,title TEXT NOT NULL,details TEXT NOT NULL,customer_email TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new','planned','shipped')),priority TEXT NOT NULL DEFAULT 'medium' CHECK(priority IN ('low','medium','high')),created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(board_id) REFERENCES boards(id) ON DELETE CASCADE);
            """)

    def register(self, workspace, slug, name, email, encoded, public_key):
        with self.db() as db:
            tenant_id = db.execute("INSERT INTO tenants(name,slug) VALUES(?,?)", (workspace, slug)).lastrowid
            user_id = db.execute("INSERT INTO users(tenant_id,name,email,password_hash) VALUES(?,?,?,?)", (tenant_id, name, email.lower(), encoded)).lastrowid
            board_id = db.execute("INSERT INTO boards(tenant_id,name,public_key) VALUES(?,?,?)", (tenant_id, "Product feedback", public_key)).lastrowid
            return {"id": user_id, "tenant_id": tenant_id, "name": name, "email": email.lower(), "workspace": workspace, "board_id": board_id, "public_key": public_key}

    def user_email(self, email):
        with self.db() as db:
            row = db.execute("SELECT u.*,t.name workspace FROM users u JOIN tenants t ON t.id=u.tenant_id WHERE u.email=?", (email.lower(),)).fetchone()
            return dict(row) if row else None

    def user_id(self, ident):
        with self.db() as db:
            row = db.execute("SELECT u.id,u.tenant_id,u.name,u.email,t.name workspace FROM users u JOIN tenants t ON t.id=u.tenant_id WHERE u.id=?", (ident,)).fetchone()
            return dict(row) if row else None

    def boards(self, tenant_id):
        with self.db() as db:
            return [dict(x) for x in db.execute("SELECT * FROM boards WHERE tenant_id=? ORDER BY created_at", (tenant_id,))]

    def submit(self, public_key, title, details, customer_email):
        with self.db() as db:
            board = db.execute("SELECT * FROM boards WHERE public_key=?", (public_key,)).fetchone()
            if not board:
                return None
            ident = db.execute("INSERT INTO feedback(tenant_id,board_id,title,details,customer_email) VALUES(?,?,?,?,?)", (board["tenant_id"], board["id"], title, details, customer_email.lower())).lastrowid
            return dict(db.execute("SELECT * FROM feedback WHERE id=?", (ident,)).fetchone())

    def list_feedback(self, tenant_id, status=None):
        with self.db() as db:
            query, args = "SELECT f.*,b.name board_name FROM feedback f JOIN boards b ON b.id=f.board_id WHERE f.tenant_id=?", [tenant_id]
            if status:
                query += " AND f.status=?"
                args.append(status)
            return [dict(x) for x in db.execute(query + " ORDER BY f.created_at DESC", args)]

    def update_feedback(self, tenant_id, ident, status, priority):
        with self.db() as db:
            changed = db.execute("UPDATE feedback SET status=?,priority=? WHERE id=? AND tenant_id=?", (status, priority, ident, tenant_id)).rowcount
            row = db.execute("SELECT * FROM feedback WHERE id=? AND tenant_id=?", (ident, tenant_id)).fetchone()
            return dict(row) if changed and row else None
