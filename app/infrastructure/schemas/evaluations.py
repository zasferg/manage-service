from app.infrastructure.schemas.base import BaseSchema
from pydantic import BaseModel, Field
from uuid import UUID


class EvaluationBase(BaseModel):
    task_id: UUID
    mark: int = Field(ge=1, le=5)


class EvaluationCreate(EvaluationBase):
    pass


class EvaluationGet(BaseSchema):
    id: UUID
    mark: int
    task_id: UUID
