from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ==========================================
# TASK STATUS
# ==========================================

class TaskStatus(str, Enum):

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    RETRY = "retry"
    FAILED = "failed"


# ==========================================
# TASK
# ==========================================

class Task(BaseModel):

    id: str

    investigation_id: str

    agent_name: str

    status: TaskStatus = TaskStatus.PENDING

    input_data: dict = Field(
        default_factory=dict
    )

    output_data: Optional[dict] = None

    depends_on: list[str] = Field(
        default_factory=list
    )

    attempts: int = 0

    max_attempts: int = 2

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )


# ==========================================
# INVESTIGATION
# ==========================================

class Investigation(BaseModel):

    id: str

    input_data: dict

    status: TaskStatus = TaskStatus.PENDING

    task_ids: list[str] = Field(
        default_factory=list
    )

    product_id: Optional[str] = None

    # Final product intelligence result
    result: Optional[dict] = None

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )