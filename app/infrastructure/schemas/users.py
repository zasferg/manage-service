from app.infrastructure.schemas.base import BaseSchema
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


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
