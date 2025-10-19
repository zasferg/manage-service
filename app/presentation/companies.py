from app.infrastructure.database.session import get_session
from app.infrastructure.schemas.companies import CompanyCreate, Company
from app.infrastructure.schemas.users import User
from app.infrastructure.services.companies import CompanyService
from app.core.permissions import user_admin_permission, user_manager_permission
from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID


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
    current_user: User = Depends(user_manager_permission),
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
    manager_permission: User = Depends(user_manager_permission),
    session: AsyncSession = Depends(get_session),
):
    try:
        if not manager_permission.company_id == company_id:
            raise ValueError("Данный менеджер не привязан к этой компании")
        company_response = await CompanyService(session).delete_user_from_company(
            user_id=user_id, company_id=company_id
        )
        company = Company.model_validate(company_response)
        return company
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))
    except ValueError as _ve:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(_ve))
