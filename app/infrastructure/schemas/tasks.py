from app.infrastructure.schemas.base import BaseSchema, ConfigDict
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.infrastructure.schemas.evaluations import EvaluationGet


class TaskBase(BaseModel):
    description: str
    deadline: Optional[datetime] = None
    company_id: UUID
    perform_user_id: UUID

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, value: datetime):
        if value and value <= datetime.now():
            raise ValueError("Сроки заверщения задачи не должны быть в прошлом")
        return value


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
    author_id: UUID
