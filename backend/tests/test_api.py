import inspect

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

import app.main as main_module


def test_production_module_does_not_create_schema():
    source = inspect.getsource(main_module)
    assert "metadata.create_all" not in source


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY"}


def test_ready_when_database_fails(client, monkeypatch):
    def fail_execute(self, *args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("database down"))

    monkeypatch.setattr(Session, "execute", fail_execute)
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == "database unavailable"


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "TaskBoard API"
    assert body["docs"] == "/docs"


def test_create_list_and_get_task(client):
    created = client.post(
        "/api/tasks",
        json={
            "title": "  Deploy application  ",
            "description": "Ship the capstone",
            "priority": "HIGH",
            "assignee": "Student",
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "Deploy application"
    assert body["status"] == "TODO"
    assert body["priority"] == "HIGH"
    assert body["id"] > 0

    listed = client.get("/api/tasks")
    assert listed.status_code == 200
    assert [task["id"] for task in listed.json()] == [body["id"]]

    fetched = client.get(f"/api/tasks/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["assignee"] == "Student"


def test_update_task(client):
    task_id = client.post("/api/tasks", json={"title": "Write tests"}).json()["id"]
    updated = client.put(
        f"/api/tasks/{task_id}",
        json={"status": "IN_PROGRESS", "priority": "LOW"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "IN_PROGRESS"
    assert updated.json()["priority"] == "LOW"
    assert updated.json()["title"] == "Write tests"


def test_delete_task(client):
    task_id = client.post("/api/tasks", json={"title": "Temporary"}).json()["id"]
    deleted = client.delete(f"/api/tasks/{task_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/api/tasks/{task_id}").status_code == 404


def test_stats_and_alias(client):
    client.post("/api/tasks", json={"title": "One", "status": "TODO"})
    client.post("/api/tasks", json={"title": "Two", "status": "IN_PROGRESS"})
    client.post("/api/tasks", json={"title": "Three", "status": "DONE"})
    expected = {"total": 3, "todo": 1, "inProgress": 1, "done": 1}
    assert client.get("/api/tasks/stats").json() == expected
    assert client.get("/api/stats").json() == expected


def test_validation_and_not_found(client):
    blank = client.post("/api/tasks", json={"title": "   "})
    assert blank.status_code == 422
    bad_priority = client.post("/api/tasks", json={"title": "Ok", "priority": "URGENT"})
    assert bad_priority.status_code == 422
    missing = client.get("/api/tasks/99999")
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Task not found"
    bad_id = client.get("/api/tasks/not-a-number")
    assert bad_id.status_code == 422
    missing_update = client.put("/api/tasks/99999", json={"title": "Nope"})
    assert missing_update.status_code == 404
    missing_delete = client.delete("/api/tasks/99999")
    assert missing_delete.status_code == 404


def test_list_filter_and_order(client):
    first = client.post("/api/tasks", json={"title": "First", "status": "TODO"}).json()["id"]
    second = client.post("/api/tasks", json={"title": "Second", "status": "DONE"}).json()["id"]
    listed = client.get("/api/tasks")
    assert [task["id"] for task in listed.json()] == [second, first]
    done = client.get("/api/tasks", params={"status": "DONE"})
    assert [task["title"] for task in done.json()] == ["Second"]


def test_metrics_expose_real_names(client):
    client.post("/api/tasks", json={"title": "Observe me", "priority": "MEDIUM"})
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    for name in (
        "http_requests_total",
        "http_request_duration_seconds",
        "taskboard_tasks_created_total",
        "taskboard_tasks_by_status",
    ):
        assert name in body
    assert 'taskboard_tasks_by_status{status="TODO"} 1.0' in body
