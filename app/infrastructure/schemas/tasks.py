from app.infrastructure.schemas.base import BaseSchema, ConfigDict
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.infrastructure.schemas.evaluations import EvaluationGet


class TaskBase(BaseModel):
    description: str
    deadline: Optional[datetime] = None
    company_id: UUID
    perform_user_id: UUID


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):

    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)
    description: Optional[str] = None
    comments: Optional[list] = None
    status: str = None
    deadline: Optional[datetime] = None
    company_id: Optional[UUID] = None
    perform_user_id: Optional[UUID] = None


class TaskGet(BaseSchema):

    description: Optional[str] = None
    status: str = None
    deadline: Optional[datetime] = None
    mark: Optional[EvaluationGet] = None
    company_id: Optional[UUID] = None
    perform_user_id: Optional[UUID] = None
