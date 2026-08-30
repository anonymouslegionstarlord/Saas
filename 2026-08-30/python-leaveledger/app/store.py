import sqlite3
from contextlib import contextmanager
from datetime import date
class Store:
    def __init__(self,path):self.path=path;self.setup()
    @contextmanager
    def db(self):
        conn=sqlite3.connect(self.path);conn.row_factory=sqlite3.Row;conn.execute("PRAGMA foreign_keys=ON")
        try:yield conn;conn.commit()
        finally:conn.close()
    def setup(self):
        with self.db() as db:db.executescript("""
        CREATE TABLE IF NOT EXISTS workspaces(id INTEGER PRIMARY KEY,name TEXT NOT NULL,annual_allowance INTEGER NOT NULL DEFAULT 24 CHECK(annual_allowance>0));
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,workspace_id INTEGER NOT NULL,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,FOREIGN KEY(workspace_id) REFERENCES workspaces(id));
        CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY,workspace_id INTEGER NOT NULL,employee_name TEXT NOT NULL,employee_email TEXT NOT NULL,leave_type TEXT NOT NULL CHECK(leave_type IN ('annual','sick','unpaid')),start_date TEXT NOT NULL,end_date TEXT NOT NULL,days INTEGER NOT NULL CHECK(days>0),reason TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(workspace_id) REFERENCES workspaces(id));
        """)
    def register(self,workspace,name,email,encoded):
        with self.db() as db:
            wid=db.execute("INSERT INTO workspaces(name) VALUES(?)",(workspace,)).lastrowid;uid=db.execute("INSERT INTO users(workspace_id,name,email,password_hash) VALUES(?,?,?,?)",(wid,name,email.lower(),encoded)).lastrowid
            return {"id":uid,"workspace_id":wid,"name":name,"email":email.lower(),"workspace":workspace}
    def user_email(self,email):
        with self.db() as db:
            row=db.execute("SELECT u.*,w.name workspace FROM users u JOIN workspaces w ON w.id=u.workspace_id WHERE u.email=?",(email.lower(),)).fetchone();return dict(row) if row else None
    def user_id(self,ident):
        with self.db() as db:
            row=db.execute("SELECT u.id,u.workspace_id,u.name,u.email,w.name workspace FROM users u JOIN workspaces w ON w.id=u.workspace_id WHERE u.id=?",(ident,)).fetchone();return dict(row) if row else None
    def create_request(self,wid,data):
        start=date.fromisoformat(data["start_date"]);end=date.fromisoformat(data["end_date"]);days=(end-start).days+1
        if days<1:raise ValueError("End date must be on or after start date")
        with self.db() as db:
            ident=db.execute("INSERT INTO requests(workspace_id,employee_name,employee_email,leave_type,start_date,end_date,days,reason) VALUES(?,?,?,?,?,?,?,?)",(wid,data["employee_name"],data["employee_email"].lower(),data["leave_type"],data["start_date"],data["end_date"],days,data["reason"])).lastrowid
            return dict(db.execute("SELECT * FROM requests WHERE id=?",(ident,)).fetchone())
    def list_requests(self,wid,status=None):
        with self.db() as db:
            query="SELECT * FROM requests WHERE workspace_id=?";args=[wid]
            if status:query+=" AND status=?";args.append(status)
            return [dict(x) for x in db.execute(query+" ORDER BY start_date DESC",args)]
    def decide(self,wid,ident,status):
        with self.db() as db:
            changed=db.execute("UPDATE requests SET status=? WHERE id=? AND workspace_id=? AND status='pending'",(status,ident,wid)).rowcount;row=db.execute("SELECT * FROM requests WHERE id=? AND workspace_id=?",(ident,wid)).fetchone();return dict(row) if changed and row else None
    def summary(self,wid):
        with self.db() as db:
            rows=db.execute("SELECT status,leave_type,days FROM requests WHERE workspace_id=?",(wid,)).fetchall()
        return {"pending":sum(1 for x in rows if x["status"]=="pending"),"approved_days":sum(x["days"] for x in rows if x["status"]=="approved"),"sick_days":sum(x["days"] for x in rows if x["status"]=="approved" and x["leave_type"]=="sick")}
