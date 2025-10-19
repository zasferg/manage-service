from app.infrastructure.schemas.base import BaseSchema
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from app.infrastructure.schemas.users import User


class MeetingBase(BaseModel):
    description: str
    meeting_starttime: datetime
    meeting_endtime: datetime
    is_cancelled: bool = Field(default=False, exclude=True)
    is_finished: bool = Field(default=False, exclude=True)

    @model_validator(mode="after")
    def validate_meeting_times(self) -> "MeetingBase":
        if self.meeting_starttime >= self.meeting_endtime:
            raise ValueError("Время окончания встречи должно быть позже времени начала")

        duration = self.meeting_endtime - self.meeting_starttime
        if duration.total_seconds() < 300:
            raise ValueError("Продолжительность встречи должна быть не менее 5 минут")

        return self


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
