from __future__ import annotations

import sqlite3
from pathlib import Path


class TaskStore:
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'todo',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_tasks_tenant ON tasks (tenant_id)")

    def list_tasks(self, tenant_id: str) -> list[dict]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT id, title, description, status, created_at FROM tasks WHERE tenant_id = ? ORDER BY id DESC",
                (tenant_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def create_task(self, tenant_id: str, title: str, description: str = "") -> dict:
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (tenant_id, title, description) VALUES (?, ?, ?)",
                (tenant_id, title.strip(), description.strip()),
            )
            task_id = cursor.lastrowid
            row = connection.execute(
                "SELECT id, title, description, status, created_at FROM tasks WHERE id = ? AND tenant_id = ?",
                (task_id, tenant_id),
            ).fetchone()
        return dict(row)

    def update_status(self, tenant_id: str, task_id: int, status: str) -> dict | None:
        with self.connect() as connection:
            cursor = connection.execute(
                "UPDATE tasks SET status = ? WHERE id = ? AND tenant_id = ?",
                (status, task_id, tenant_id),
            )
            if cursor.rowcount == 0:
                return None
            row = connection.execute(
                "SELECT id, title, description, status, created_at FROM tasks WHERE id = ? AND tenant_id = ?",
                (task_id, tenant_id),
            ).fetchone()
        return dict(row)

    def delete_task(self, tenant_id: str, task_id: int) -> bool:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM tasks WHERE id = ? AND tenant_id = ?", (task_id, tenant_id))
        return cursor.rowcount > 0
