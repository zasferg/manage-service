from app.infrastructure.schemas.base import BaseSchema
from app.core.validators.password_validator import PasswordValidator
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from typing import Optional


class UserBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        return PasswordValidator.validate_and_raise(value)

class UserUpdate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[UUID] = None

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        return PasswordValidator.validate_and_raise(value)


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
