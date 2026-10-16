from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (Index("ix_tasks_status", "status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM", server_default="MEDIUM")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="TODO", server_default="TODO")
    assignee: Mapped[str] = mapped_column(String(120), nullable=False, default="Unassigned", server_default="Unassigned")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
