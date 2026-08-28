import sqlite3
from contextlib import contextmanager
from datetime import date

class Store:
    def __init__(self,path):
        self.path=path
        self.setup()

    @contextmanager
    def db(self):
        connection=sqlite3.connect(self.path)
        connection.row_factory=sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def setup(self):
        with self.db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS workspaces(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,workspace_id INTEGER NOT NULL,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,FOREIGN KEY(workspace_id) REFERENCES workspaces(id));
            CREATE TABLE IF NOT EXISTS subscriptions(id INTEGER PRIMARY KEY,workspace_id INTEGER NOT NULL,vendor TEXT NOT NULL,category TEXT NOT NULL,cost REAL NOT NULL CHECK(cost>=0),billing_cycle TEXT NOT NULL CHECK(billing_cycle IN ('monthly','quarterly','yearly')),renewal_date TEXT NOT NULL,owner TEXT NOT NULL,notes TEXT NOT NULL DEFAULT '',active INTEGER NOT NULL DEFAULT 1,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(workspace_id) REFERENCES workspaces(id));
            """)

    def register(self,workspace,name,email,encoded):
        with self.db() as db:
            wid=db.execute("INSERT INTO workspaces(name) VALUES(?)",(workspace,)).lastrowid
            uid=db.execute("INSERT INTO users(workspace_id,name,email,password_hash) VALUES(?,?,?,?)",(wid,name,email.lower(),encoded)).lastrowid
            return {"id":uid,"workspace_id":wid,"name":name,"email":email.lower(),"workspace":workspace}

    def user_by_email(self,email):
        with self.db() as db:
            row=db.execute("SELECT u.*,w.name workspace FROM users u JOIN workspaces w ON w.id=u.workspace_id WHERE u.email=?",(email.lower(),)).fetchone()
            return dict(row) if row else None

    def user_by_id(self,ident):
        with self.db() as db:
            row=db.execute("SELECT u.id,u.workspace_id,u.name,u.email,w.name workspace FROM users u JOIN workspaces w ON w.id=u.workspace_id WHERE u.id=?",(ident,)).fetchone()
            return dict(row) if row else None

    def create_subscription(self,wid,data):
        with self.db() as db:
            ident=db.execute("INSERT INTO subscriptions(workspace_id,vendor,category,cost,billing_cycle,renewal_date,owner,notes) VALUES(?,?,?,?,?,?,?,?)",(wid,data["vendor"],data["category"],data["cost"],data["billing_cycle"],data["renewal_date"],data["owner"],data["notes"])).lastrowid
            return dict(db.execute("SELECT * FROM subscriptions WHERE id=?",(ident,)).fetchone())

    def list_subscriptions(self,wid):
        with self.db() as db:
            return [dict(row) for row in db.execute("SELECT * FROM subscriptions WHERE workspace_id=? ORDER BY renewal_date",(wid,))]

    def update_subscription(self,wid,ident,active):
        with self.db() as db:
            changed=db.execute("UPDATE subscriptions SET active=? WHERE id=? AND workspace_id=?",(int(active),ident,wid)).rowcount
            row=db.execute("SELECT * FROM subscriptions WHERE id=? AND workspace_id=?",(ident,wid)).fetchone()
            return dict(row) if changed and row else None

    def delete_subscription(self,wid,ident):
        with self.db() as db:
            return db.execute("DELETE FROM subscriptions WHERE id=? AND workspace_id=?",(ident,wid)).rowcount==1

    def summary(self,wid):
        with self.db() as db:
            rows=db.execute("SELECT cost,billing_cycle,renewal_date FROM subscriptions WHERE workspace_id=? AND active=1",(wid,)).fetchall()
        annual=sum(r["cost"]*{"monthly":12,"quarterly":4,"yearly":1}[r["billing_cycle"]] for r in rows)
        upcoming=sum(1 for r in rows if 0<=(date.fromisoformat(r["renewal_date"])-date.today()).days<=30)
        return {"active":len(rows),"annual_spend":round(annual,2),"renewing_within_30_days":upcoming}
