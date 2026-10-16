from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Status = Literal["TODO", "IN_PROGRESS", "DONE"]
Priority = Literal["LOW", "MEDIUM", "HIGH"]


def _required_title(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("title cannot be blank")
    return cleaned


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    priority: Priority = "MEDIUM"
    status: Status = "TODO"
    assignee: str = Field(default="Unassigned", min_length=1, max_length=120)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        return _required_title(value)

    @field_validator("assignee")
    @classmethod
    def assignee_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("assignee cannot be blank")
        return cleaned


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    priority: Priority | None = None
    status: Status | None = None
    assignee: str | None = Field(default=None, min_length=1, max_length=120)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _required_title(value)

    @field_validator("assignee")
    @classmethod
    def assignee_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("assignee cannot be blank")
        return cleaned


class TaskOut(TaskCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StatsOut(BaseModel):
    total: int
    todo: int
    inProgress: int
    done: int
