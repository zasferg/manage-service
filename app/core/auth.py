import jwt
from datetime import timedelta
from typing import Optional
from fastapi import HTTPException
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from datetime import datetime
from infrastructure.repositories.users import UserRepository
from infrastructure.repositories.tokens import TokenRepository
import bcrypt
from core.config import settings


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = timedelta(
        minutes=int(settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    ),
) -> str:
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = timedelta(
        minutes=int(settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    ),
) -> str:
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise credentials_exception


def get_token_data(token: str) -> dict:
    payload = verify_token(token)
    if payload:
        return payload
    return {}


async def get_checked_token_data(
    token: str, session: AsyncSession, refresh: bool = False
) -> dict:
    payload = verify_token(token)
    if not payload or "user_id" not in payload:
        return {}
    if not await UserRepository(session).get_by_id(id=payload["user_id"]):
        return {}
    if refresh and not await TokenRepository(session).get_filtered_by_params(
        user_id=payload["user_id"], refresh_token=token
    ):
        return {}
    return payload


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")
