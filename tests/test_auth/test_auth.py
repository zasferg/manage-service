import pytest
from infrastructure.authentication.auth import access_token_auth
from infrastructure.repositories.users import UserRepository
from infrastructure.services.users import UsersService
from fastapi.security import HTTPAuthorizationCredentials
from core.auth import hash_password
from main import app


@pytest.mark.asyncio
async def test_registration(
    test_user, 
    test_session
):
    user_result = await UsersService(test_session).user_register(test_user)

    assert user_result.status_code == 201
    assert user_result.body ==  b'{"message":"Registration successful"}'


@pytest.mark.asyncio
async def test_login_and_logout(test_session, test_user):
    await UserRepository(test_session).create(
        email=test_user.email, password=hash_password(test_user.password)
    )

    result_from_login = await UsersService(test_session).user_login(test_user)
    access_token = result_from_login["access_token"]

    assert access_token is not None
    assert result_from_login["token_type"] == "bearer"

    auth_credentials = HTTPAuthorizationCredentials(
    scheme="Bearer",
    credentials=access_token
    )
    authenticated_user = await access_token_auth(
        session=test_session, 
        token = auth_credentials
    )
    result_from_logout = await UsersService(test_session).user_logout(current_user_data=authenticated_user)

    assert result_from_logout.status_code == 204
    assert result_from_logout.body ==  b'{"detail":"Logout"}'
