from app.infrastructure.schemas.base import BaseSchema
from app.infrastructure.schemas.users import User
from pydantic import BaseModel
from typing import Optional, List


class CompanyBase(BaseModel):
    name: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class Company(CompanyBase, BaseSchema):
    users: Optional[List["User"]] = None
