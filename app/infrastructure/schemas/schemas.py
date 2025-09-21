from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from core.enums import RolesEnum, TaskStatuses
from typing import Optional, List


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created: datetime
    updated_on: datetime


class UserBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[UUID] = None

class UserInternal(BaseSchema):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[UUID] = None

class User(UserInternal, BaseSchema):
    # company_id: Optional[UUID] = None
    # company: Optional["Company"] = None
    pass


class UserForLogin(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class CompanyBase(BaseModel):
    name: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class Company(CompanyBase, BaseSchema):
    users: Optional[List["User"]] = None


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
    mark: Optional[int] = None
    company_id: Optional[UUID] = None
    perform_user_id: Optional[UUID] = None


class TaskGet(BaseSchema):

    model_config = ConfigDict(from_attributes=True)

    description: Optional[str] = None
    # comments: Optional[str] = None
    status: str = None
    deadline: Optional[datetime] = None
    mark: Optional[int] = None
    company_id: Optional[UUID] = None
    perform_user_id: Optional[UUID] = None


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


class RatingRequest(BaseModel):
    rating: int = Field(ge=1, le=5)


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
