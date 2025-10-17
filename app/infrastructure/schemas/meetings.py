from app.infrastructure.schemas.base import BaseSchema
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, List
from app.infrastructure.schemas.users import User


class MeetingBase(BaseModel):
    description: str
    meeting_starttime: datetime
    meeting_endtime: datetime
    is_cancelled: bool = Field(default=False, exclude=True)
    is_finished: bool = Field(default=False, exclude=True)


class MeetingCreate(MeetingBase):
    pass


class MeetingUpdate(BaseModel):
    is_cancelled: Optional[bool] = None
    is_finished: Optional[bool] = None
    description: Optional[str] = None
    meeting_datetime: Optional[datetime] = None


class Meeting(MeetingBase, BaseSchema):
    pass


class MeetingWithRelations(Meeting):
    user_meetings: List["UserMeetingRelationResponse"] = []


class UserMeetingRelationBase(BaseModel):
    user_id: UUID
    meeting_id: UUID


class UserMeetingRelationCreate(UserMeetingRelationBase):
    pass


class UserMeetingRelationResponse(UserMeetingRelationBase, BaseSchema):
    pass


class UserMeetingRelationWithRelations(UserMeetingRelationResponse):
    user: Optional[User] = None
    meeting: Optional[Meeting] = None
