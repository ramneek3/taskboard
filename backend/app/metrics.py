from prometheus_client import REGISTRY, Counter
from prometheus_client.metrics_core import GaugeMetricFamily
from sqlalchemy import func, select

from .db import SessionLocal
from .models import Task

TASKS_CREATED = Counter(
    "taskboard_tasks_created_total",
    "Tasks created through the API",
    ["priority"],
)
TASKS_UPDATED = Counter(
    "taskboard_tasks_updated_total",
    "Tasks updated through the API",
)
TASKS_DELETED = Counter(
    "taskboard_tasks_deleted_total",
    "Tasks deleted through the API",
)

STATUSES = ("TODO", "IN_PROGRESS", "DONE")


class TaskStatusCollector:
    """Read task counts at scrape time so the gauge matches the database."""

    def collect(self):
        counts = {status: 0 for status in STATUSES}
        try:
            db = SessionLocal()
            try:
                rows = db.execute(select(Task.status, func.count(Task.id)).group_by(Task.status)).all()
                for status, count in rows:
                    if status in counts:
                        counts[status] = int(count)
            finally:
                db.close()
        except Exception:
            # Metrics must stay available when the database is down.
            pass
        metric = GaugeMetricFamily(
            "taskboard_tasks_by_status",
            "Tasks currently stored, labeled by status",
            labels=["status"],
        )
        for status, count in counts.items():
            metric.add_metric([status], count)
        yield metric


def register_collectors() -> None:
    collectors = getattr(REGISTRY, "_collector_to_names", {})
    if any(isinstance(collector, TaskStatusCollector) for collector in collectors):
        return
    REGISTRY.register(TaskStatusCollector())


register_collectors()
