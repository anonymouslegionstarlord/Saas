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
        with self.db() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS workspaces(id INTEGER PRIMARY KEY,name TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,workspace_id INTEGER NOT NULL,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,FOREIGN KEY(workspace_id) REFERENCES workspaces(id));
            CREATE TABLE IF NOT EXISTS policies(id INTEGER PRIMARY KEY,workspace_id INTEGER NOT NULL,title TEXT NOT NULL,version TEXT NOT NULL,content TEXT NOT NULL,public_key TEXT UNIQUE NOT NULL,active INTEGER NOT NULL DEFAULT 1,created_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(workspace_id,title,version),FOREIGN KEY(workspace_id) REFERENCES workspaces(id));
            CREATE TABLE IF NOT EXISTS acknowledgements(id INTEGER PRIMARY KEY,workspace_id INTEGER NOT NULL,policy_id INTEGER NOT NULL,employee_name TEXT NOT NULL,employee_email TEXT NOT NULL,accepted_at TEXT DEFAULT CURRENT_TIMESTAMP,UNIQUE(policy_id,employee_email),FOREIGN KEY(policy_id) REFERENCES policies(id) ON DELETE CASCADE);
            """)
    def register(self,workspace,name,email,encoded):
        with self.db() as db:
            wid=db.execute("INSERT INTO workspaces(name) VALUES(?)",(workspace,)).lastrowid
            uid=db.execute("INSERT INTO users(workspace_id,name,email,password_hash) VALUES(?,?,?,?)",(wid,name,email.lower(),encoded)).lastrowid
            return {"id":uid,"workspace_id":wid,"name":name,"email":email.lower(),"workspace":workspace}
    def user_email(self,email):
        with self.db() as db:
            row=db.execute("SELECT u.*,w.name workspace FROM users u JOIN workspaces w ON w.id=u.workspace_id WHERE u.email=?",(email.lower(),)).fetchone();return dict(row) if row else None
    def user_id(self,ident):
        with self.db() as db:
            row=db.execute("SELECT u.id,u.workspace_id,u.name,u.email,w.name workspace FROM users u JOIN workspaces w ON w.id=u.workspace_id WHERE u.id=?",(ident,)).fetchone();return dict(row) if row else None
    def create_policy(self,wid,title,version,content,key):
        with self.db() as db:
            ident=db.execute("INSERT INTO policies(workspace_id,title,version,content,public_key) VALUES(?,?,?,?,?)",(wid,title,version,content,key)).lastrowid
            return dict(db.execute("SELECT * FROM policies WHERE id=?",(ident,)).fetchone())
    def list_policies(self,wid):
        with self.db() as db:
            return [dict(x) for x in db.execute("SELECT p.*,COUNT(a.id) acknowledgement_count FROM policies p LEFT JOIN acknowledgements a ON a.policy_id=p.id WHERE p.workspace_id=? GROUP BY p.id ORDER BY p.created_at DESC",(wid,))]
    def public_policy(self,key):
        with self.db() as db:
            row=db.execute("SELECT id,title,version,content,public_key FROM policies WHERE public_key=? AND active=1",(key,)).fetchone();return dict(row) if row else None
    def acknowledge(self,key,name,email):
        with self.db() as db:
            policy=db.execute("SELECT * FROM policies WHERE public_key=? AND active=1",(key,)).fetchone()
            if not policy:return None
            ident=db.execute("INSERT INTO acknowledgements(workspace_id,policy_id,employee_name,employee_email) VALUES(?,?,?,?)",(policy["workspace_id"],policy["id"],name,email.lower())).lastrowid
            return dict(db.execute("SELECT * FROM acknowledgements WHERE id=?",(ident,)).fetchone())
    def acknowledgements(self,wid,policy_id):
        with self.db() as db:
            owned=db.execute("SELECT id FROM policies WHERE id=? AND workspace_id=?",(policy_id,wid)).fetchone()
            return None if not owned else [dict(x) for x in db.execute("SELECT * FROM acknowledgements WHERE policy_id=? ORDER BY accepted_at DESC",(policy_id,))]
    def toggle(self,wid,ident,active):
        with self.db() as db:
            changed=db.execute("UPDATE policies SET active=? WHERE id=? AND workspace_id=?",(int(active),ident,wid)).rowcount
            row=db.execute("SELECT * FROM policies WHERE id=? AND workspace_id=?",(ident,wid)).fetchone();return dict(row) if changed and row else None
