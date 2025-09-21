from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from core.auth import create_access_token, create_refresh_token, get_checked_token_data
from infrastructure.schemas.schemas import *
from infrastructure.repositories.tokens import TokenRepository
from infrastructure.authentication.auth import access_token_auth
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.session import get_session
from infrastructure.services.users import UsersService


auth = APIRouter(
    prefix="/auth",
    tags=[
        "auth",
    ],
)


@auth.post("/registration")
async def registration_handler(
    user_data: UserCreate, session: AsyncSession = Depends(get_session)
):
    try:
        result = await UsersService(session).user_register(user_data)
        return result
    except Exception as _e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(_e))


@auth.post("/login")
async def login_for_access_token(
    user_data: UserForLogin, session: AsyncSession = Depends(get_session)
):
    try:
        result = await UsersService(session).user_login(user_data)
        return result
    except Exception as _e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(_e))


@auth.post("/logout")
async def logout(
    current_user: dict = Depends(access_token_auth),
    session: AsyncSession = Depends(get_session),
):
    try:
        result = await UsersService(session).user_logout(current_user)
        return result
    except Exception as _e:
        raise HTTPException(status_code=400, detail=str(_e))


@auth.post("/get_access")
async def get_access_handler(
    refresh_token: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    try:
        payload = await get_checked_token_data(
            token=refresh_token, session=session, refresh=True
        )
        if not payload:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Неверный токен"
            )

        access_token = create_access_token(data={"user_id": str(payload["user_id"])})
        refresh_token = create_refresh_token(data={"user_id": str(payload["user_id"])})
        await TokenRepository(session).create(
            refresh_token=refresh_token, user_id=payload["user_id"]
        )

        return {"access_token": access_token, "refresh_token": refresh_token}
    except HTTPException as _he:
        raise HTTPException(status_code=_he.status_code, detail=f"Токен истек, {_he}")
    except Exception as _e:
        raise HTTPException(status_code=400, detail=str(_e))
