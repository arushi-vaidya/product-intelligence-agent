from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class Task(BaseModel):
    id: str
    investigation_id: str

    agent_name: str
    status: TaskStatus = TaskStatus.PENDING

    input_data: dict = {}
    output_data: Optional[dict] = None

    depends_on: list[str] = []

    attempts: int = 0
    max_attempts: int = 2

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Investigation(BaseModel):
    id: str

    input_data: dict

    status: TaskStatus = TaskStatus.PENDING

    task_ids: list[str] = []

    product_id: Optional[str] = None