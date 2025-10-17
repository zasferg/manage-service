from app.infrastructure.schemas.base import BaseSchema
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class CommentCreate(BaseModel):
    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)
    task_id: UUID
    text: str
    to_user_id: UUID
    from_user_id: Optional[UUID] = Field(exclude=True, default=None)


class CommentGet(CommentCreate, BaseSchema):
    pass


class CommentEntity(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    task_id: UUID
    text: str
    from_user_id: UUID
    to_user_id: UUID
    parent_id: Optional[UUID] = None
    created: Optional[datetime] = None
