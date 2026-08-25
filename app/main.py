from __future__ import annotations

import os
from functools import lru_cache
from typing import Annotated, Literal

from fastapi import FastAPI, Header, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.store import TaskStore

app = FastAPI(title="Tenant Tasks", version="1.0.0", description="A small tenant-aware task SaaS API")
TenantHeader = Annotated[str, Header(alias="X-Tenant-ID", min_length=2, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)


class TaskStatus(BaseModel):
    status: Literal["todo", "doing", "done"]


@lru_cache
def get_store() -> TaskStore:
    return TaskStore(os.getenv("DATABASE_PATH", "tenant_tasks.db"))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/tasks")
def list_tasks(tenant_id: TenantHeader) -> list[dict]:
    return get_store().list_tasks(tenant_id)


@app.post("/api/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, tenant_id: TenantHeader) -> dict:
    return get_store().create_task(tenant_id, payload.title, payload.description)


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, payload: TaskStatus, tenant_id: TenantHeader) -> dict:
    task = get_store().update_status(tenant_id, task_id, payload.status)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, tenant_id: TenantHeader) -> Response:
    if not get_store().delete_task(tenant_id, task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
