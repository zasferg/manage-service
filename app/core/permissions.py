from infrastructure.authentication.auth import access_token_auth
from infrastructure.repositories.users import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from core.enums import RolesEnum
from infrastructure.database.session import get_session
from typing import Annotated
from infrastructure.schemas.schemas import *


permissons_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Forbidden",
)


async def user_manager_permission(
    current_user=Depends(access_token_auth),
    session: AsyncSession = Annotated[AsyncSession, Depends(get_session)],
):
    user = UserRepository(session).get_by_id(id=current_user["user"].id)

    if not user.role == RolesEnum.MANAGER:
        raise permissons_exception

    return user


async def user_manager_permission(
    current_user: dict = Depends(access_token_auth),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        user = await UserRepository(session).get_by_id(id=current_user["user"].id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if user.role == RolesEnum.ADMIN:
            return User.model_validate(user)
        if user.role != RolesEnum.MANAGER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions. Manager role required",
            )

        return User.model_validate(user)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Permission check error: {str(e)}",
        )


async def user_admin_permission(
    current_user: dict = Depends(access_token_auth),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        user = await UserRepository(session).get_by_id(id=current_user["user"].id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.role != RolesEnum.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions. Admin role required",
            )

        return User.model_validate(user)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Permission check error: {str(e)}",
        )
