from fastapi.security import HTTPAuthorizationCredentials
import pytest
from app.infrastructure.services.users import UsersService
from app.infrastructure.authentication.auth import access_token_auth
from app.infrastructure.repositories.users import UserRepository
from app.infrastructure.repositories.tokens import TokenRepository
from app.core.auth import hash_password, create_access_token, create_refresh_token
from app.infrastructure.schemas.schemas import UserUpdate, User
from app.core.enums import RolesEnum


@pytest.mark.asyncio
async def test_get_user(test_session, test_user):
    user = await UserRepository(test_session).create(
        email=test_user.email, password=hash_password(test_user.password)
    )
    user_prepared = User.model_validate(user)

    access_token = create_access_token(data={"user_id": str(user.id)})
    refresh_token = create_refresh_token(data={"user_id": str(user.id)})
    await TokenRepository(test_session).create(
        refresh_token=refresh_token, user_id=user.id
    )

    auth_credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=access_token
    )
    authenticated_user = await access_token_auth(
        session=test_session, token=auth_credentials
    )
    current_user = await UsersService(test_session).get_current_user(
        current_user=authenticated_user
    )
    assert current_user.email == user_prepared.email


@pytest.mark.asyncio
async def test_update_user(test_session, test_user):

    user = await UserRepository(test_session).create(
        email=test_user.email, password=hash_password(test_user.password)
    )
    old_user = User.model_validate(user)

    new_data = UserUpdate(email="newtestemail@test.com", role=RolesEnum.ADMIN)
    access_token = create_access_token(data={"user_id": str(user.id)})
    refresh_token = create_refresh_token(data={"user_id": str(user.id)})

    await TokenRepository(test_session).create(
        refresh_token=refresh_token, user_id=user.id
    )
    auth_credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=access_token
    )
    authenticated_user = await access_token_auth(
        session=test_session, token=auth_credentials
    )
    updated_user = await UsersService(test_session).update_current_user(
        current_user=authenticated_user, update_data=new_data
    )

    assert updated_user.email == new_data.email
    assert updated_user.role == new_data.role


@pytest.mark.asyncio
async def test_delete_user(test_session, test_user):
    user = await UserRepository(test_session).create(
        email=test_user.email, password=hash_password(test_user.password)
    )
    user_prepared = User.model_validate(user)

    access_token = create_access_token(data={"user_id": str(user.id)})
    refresh_token = create_refresh_token(data={"user_id": str(user.id)})

    await TokenRepository(test_session).create(
        refresh_token=refresh_token, user_id=user.id
    )

    auth_credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=access_token
    )
    authenticated_user = await access_token_auth(
        session=test_session, token=auth_credentials
    )

    await UsersService(test_session).delete_current_user(
        current_user=authenticated_user
    )

    user = await UserRepository(test_session).get_by_id(id=user_prepared.id)

    assert user is None
