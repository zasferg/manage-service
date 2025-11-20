from app.infrastructure.authentication.auth import access_token_auth
from app.infrastructure.repositories.users import UserRepository
from app.infrastructure.database.session import get_session
from app.infrastructure.schemas.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from app.core.enums import RolesEnum


permissons_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Forbidden",
)


async def user_manager_permission(
    current_user=Depends(access_token_auth),
    session: AsyncSession = Depends(get_session),
) -> User:
    user = await UserRepository(session).get_by_id(id=current_user["user"].id)

    if user.role == RolesEnum.MANAGER or user.role == RolesEnum.ADMIN:
        return user
    else:
        raise permissons_exception


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
            raise permissons_exception

        return User.model_validate(user)

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Permission check error: {str(e)}",
        )
