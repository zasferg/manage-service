from typing import Annotated
from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_token_data, credentials_exception
from app.infrastructure.repositories.users import UserRepository
from app.infrastructure.database.session import get_session

security = HTTPBearer()


async def access_token_auth(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: AsyncSession = Depends(get_session),
):
    payload = get_token_data(token.credentials)
    user_id = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    user = await UserRepository(session).get_by_id(id=user_id)
    if not user:
        raise credentials_exception
    return {"user": user, "payload": payload, "token": token.credentials}
