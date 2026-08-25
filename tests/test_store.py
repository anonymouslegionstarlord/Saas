from pathlib import Path

from app.store import TaskStore


def test_tasks_are_isolated_by_tenant(tmp_path: Path) -> None:
    store = TaskStore(tmp_path / "test.db")
    store.create_task("alpha", "Alpha task")
    store.create_task("beta", "Beta task")
    assert [task["title"] for task in store.list_tasks("alpha")] == ["Alpha task"]
    assert [task["title"] for task in store.list_tasks("beta")] == ["Beta task"]


def test_update_and_delete_are_tenant_scoped(tmp_path: Path) -> None:
    store = TaskStore(tmp_path / "test.db")
    task = store.create_task("alpha", "Scoped task")
    assert store.update_status("beta", task["id"], "done") is None
    assert store.update_status("alpha", task["id"], "done")["status"] == "done"
    assert store.delete_task("beta", task["id"]) is False
    assert store.delete_task("alpha", task["id"]) is True
