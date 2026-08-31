import sqlite3
from contextlib import contextmanager
class Store:
    def __init__(self,path):self.path=path;self.setup()
    @contextmanager
    def db(self):
        conn=sqlite3.connect(self.path);conn.row_factory=sqlite3.Row;conn.execute("PRAGMA foreign_keys=ON")
        try:yield conn;conn.commit()
        finally:conn.close()
    def setup(self):
        with self.db() as db:db.executescript("""
        CREATE TABLE IF NOT EXISTS workspaces(id INTEGER PRIMARY KEY,name TEXT NOT NULL,status_key TEXT UNIQUE NOT NULL);
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,workspace_id INTEGER NOT NULL,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,FOREIGN KEY(workspace_id) REFERENCES workspaces(id));
        CREATE TABLE IF NOT EXISTS incidents(id INTEGER PRIMARY KEY,workspace_id INTEGER NOT NULL,title TEXT NOT NULL,severity TEXT NOT NULL CHECK(severity IN ('minor','major','critical')),status TEXT NOT NULL DEFAULT 'investigating' CHECK(status IN ('investigating','identified','monitoring','resolved')),summary TEXT NOT NULL,started_at TEXT DEFAULT CURRENT_TIMESTAMP,resolved_at TEXT,FOREIGN KEY(workspace_id) REFERENCES workspaces(id));
        CREATE TABLE IF NOT EXISTS updates(id INTEGER PRIMARY KEY,workspace_id INTEGER NOT NULL,incident_id INTEGER NOT NULL,status TEXT NOT NULL,message TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(incident_id) REFERENCES incidents(id) ON DELETE CASCADE);
        """)
    def register(self,workspace,key,name,email,encoded):
        with self.db() as db:
            wid=db.execute("INSERT INTO workspaces(name,status_key) VALUES(?,?)",(workspace,key)).lastrowid;uid=db.execute("INSERT INTO users(workspace_id,name,email,password_hash) VALUES(?,?,?,?)",(wid,name,email.lower(),encoded)).lastrowid
            return {"id":uid,"workspace_id":wid,"name":name,"email":email.lower(),"workspace":workspace,"status_key":key}
    def user_email(self,email):
        with self.db() as db:
            row=db.execute("SELECT u.*,w.name workspace FROM users u JOIN workspaces w ON w.id=u.workspace_id WHERE u.email=?",(email.lower(),)).fetchone();return dict(row) if row else None
    def user_id(self,ident):
        with self.db() as db:
            row=db.execute("SELECT u.id,u.workspace_id,u.name,u.email,w.name workspace,w.status_key FROM users u JOIN workspaces w ON w.id=u.workspace_id WHERE u.id=?",(ident,)).fetchone();return dict(row) if row else None
    def create_incident(self,wid,data):
        with self.db() as db:
            ident=db.execute("INSERT INTO incidents(workspace_id,title,severity,summary) VALUES(?,?,?,?)",(wid,data["title"],data["severity"],data["summary"])).lastrowid
            db.execute("INSERT INTO updates(workspace_id,incident_id,status,message) VALUES(?,?,?,?)",(wid,ident,"investigating",data["summary"]))
            return dict(db.execute("SELECT * FROM incidents WHERE id=?",(ident,)).fetchone())
    def list_incidents(self,wid):
        with self.db() as db:return [dict(x) for x in db.execute("SELECT i.*,COUNT(u.id) update_count FROM incidents i LEFT JOIN updates u ON u.incident_id=i.id WHERE i.workspace_id=? GROUP BY i.id ORDER BY i.started_at DESC",(wid,))]
    def add_update(self,wid,ident,status,message):
        with self.db() as db:
            owned=db.execute("SELECT id FROM incidents WHERE id=? AND workspace_id=?",(ident,wid)).fetchone()
            if not owned:return None
            db.execute("UPDATE incidents SET status=?,resolved_at=CASE WHEN ?='resolved' THEN CURRENT_TIMESTAMP ELSE NULL END WHERE id=?",(status,status,ident))
            update_id=db.execute("INSERT INTO updates(workspace_id,incident_id,status,message) VALUES(?,?,?,?)",(wid,ident,status,message)).lastrowid
            return dict(db.execute("SELECT * FROM updates WHERE id=?",(update_id,)).fetchone())
    def public_status(self,key):
        with self.db() as db:
            workspace=db.execute("SELECT * FROM workspaces WHERE status_key=?",(key,)).fetchone()
            if not workspace:return None
            incidents=[dict(x) for x in db.execute("SELECT * FROM incidents WHERE workspace_id=? ORDER BY started_at DESC LIMIT 20",(workspace["id"],))]
            for incident in incidents:incident["updates"]=[dict(x) for x in db.execute("SELECT status,message,created_at FROM updates WHERE incident_id=? ORDER BY created_at DESC",(incident["id"],))]
            return {"workspace":workspace["name"],"incidents":incidents}
