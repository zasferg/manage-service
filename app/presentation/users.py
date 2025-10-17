from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.schemas.users import UserUpdate
from app.infrastructure.database.session import get_session
from app.infrastructure.services.users import UsersService
from app.infrastructure.authentication.auth import access_token_auth
from starlette.status import HTTP_400_BAD_REQUEST
from fastapi import HTTPException


users = APIRouter(
    prefix="/users",
    tags=["Юзеры"],
)


@users.get("/me")
async def get_users_info(
    current_user: dict = Depends(access_token_auth),
    session: AsyncSession = Depends(get_session),
):
    try:
        current_user = await UsersService(session).get_current_user(current_user)
        return current_user
    except Exception as _e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(_e))


@users.put("/me")
async def update_users_info(
    update_data: UserUpdate,
    current_user: dict = Depends(access_token_auth),
    session: AsyncSession = Depends(get_session),
):
    try:
        updated_user = await UsersService(session).update_current_user(
            update_data=update_data, current_user=current_user
        )
        return updated_user

    except Exception as _e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(_e))


@users.delete("/me")
async def delete_user(
    current_user: dict = Depends(access_token_auth),
    session: AsyncSession = Depends(get_session),
):
    try:
        result = await UsersService(session).delete_current_user(
            current_user=current_user
        )
        return result
    except Exception as _e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(_e))
