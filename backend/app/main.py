from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from . import metrics
from .config import settings
from .db import get_db
from .models import Task
from .schemas import Priority, StatsOut, Status, TaskCreate, TaskOut, TaskUpdate


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Schema changes belong to Alembic. Startup does not create tables.
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


def _stats(db: Session) -> StatsOut:
    rows = db.execute(select(Task.status, func.count(Task.id)).group_by(Task.status)).all()
    counts = {row_status: count for row_status, count in rows}
    todo = int(counts.get("TODO", 0))
    in_progress = int(counts.get("IN_PROGRESS", 0))
    done = int(counts.get("DONE", 0))
    return StatsOut(total=todo + in_progress + done, todo=todo, inProgress=in_progress, done=done)


def _get_or_404(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "metrics": "/metrics",
    }


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="database unavailable") from exc
    return {"status": "READY"}


@app.get("/api/stats", response_model=StatsOut)
@app.get("/api/tasks/stats", response_model=StatsOut)
def task_stats(db: Session = Depends(get_db)):
    return _stats(db)


@app.get("/api/tasks", response_model=list[TaskOut])
def list_tasks(
    status_filter: Status | None = Query(default=None, alias="status"),
    priority: Priority | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Task).order_by(Task.id.desc())
    if status_filter is not None:
        statement = statement.where(Task.status == status_filter)
    if priority is not None:
        statement = statement.where(Task.priority == priority)
    return list(db.scalars(statement))


@app.get("/api/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, task_id)


@app.post("/api/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    metrics.TASKS_CREATED.labels(priority=task.priority).inc()
    return task


@app.put("/api/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = _get_or_404(db, task_id)
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    metrics.TASKS_UPDATED.inc()
    return task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = _get_or_404(db, task_id)
    db.delete(task)
    db.commit()
    metrics.TASKS_DELETED.inc()
