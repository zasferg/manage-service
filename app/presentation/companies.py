from fastapi import APIRouter, Depends
from infrastructure.schemas.schemas import *
from infrastructure.services.companies import CompanyService
from core.permissions import user_admin_permission, user_manager_permission
from infrastructure.authentication.auth import access_token_auth
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.session import get_session
from typing import Annotated
from fastapi import HTTPException, status

companies = APIRouter(
    prefix="/companies",
    tags=[
        "Компании",
    ],
)


@companies.post(
    "/create",
)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(user_admin_permission),
    session: AsyncSession = Depends(get_session),
):
    try:
        company = await CompanyService(session).create_company(company_data)
        return company
    except Exception as e:
        raise (str(e))


@companies.get(
    "/get",
)
async def get_company(
    id: UUID,
    session: AsyncSession = Depends(get_session),
):
    try:
        if id:
            company_response = await CompanyService(session).get_company(id)
        if not company_response:
            raise Exception
        company = Company.model_validate(company_response)
        return company
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))


@companies.put(
    "/add_user",
)
async def add_user_to_company(
    user_id: UUID,
    company_id: UUID,
    current_user: User = Depends(user_admin_permission),
    session: AsyncSession = Depends(get_session),
):
    try:
        company_response = await CompanyService(session).add_user_to_company(
            user_id=user_id, company_id=company_id
        )
        company = Company.model_validate(company_response)
        return company
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))


@companies.put(
    "/delete_user",
)
async def delete_user_to_company(
    user_id: UUID,
    company_id: UUID,
    current_user: User = Depends(user_admin_permission),
    session: AsyncSession = Depends(get_session),
):
    try:
        company_response = await CompanyService(session).delete_user_from_company(
            user_id=user_id, company_id=company_id
        )
        company = Company.model_validate(company_response)
        return company
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))
