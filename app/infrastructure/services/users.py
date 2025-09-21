from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_201_CREATED,
)
from core.auth import create_access_token, create_refresh_token
from infrastructure.schemas.schemas import *
from infrastructure.repositories.users import UserRepository
from infrastructure.repositories.tokens import TokenRepository

from sqlalchemy.ext.asyncio import AsyncSession
from core.auth import verify_password, hash_password


class UsersService:
    def __init__(self, async_session: AsyncSession):
        self.session = async_session

    async def user_register(self, user_data: UserCreate):

        try:
            user_by_email = await UserRepository(self.session).get_filtered_by_params(
                email=user_data.email
            )
            if user_by_email:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="User exists",
                )
            user = await UserRepository(self.session).create(
                email=user_data.email, password=hash_password(user_data.password)
            )
            create_access_token(data={"user_id": str(user.id)})
            refresh_token = create_refresh_token(data={"user_id": str(user.id)})
            await TokenRepository(self.session).create(
                refresh_token=refresh_token, user_id=user.id
            )
            return JSONResponse(
                status_code=HTTP_201_CREATED,
                content={"message": "Registration successful"},
            )

        except IntegrityError as _ie:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Wrong data type, {_ie}",
            )

    async def user_login(self, user_data: UserForLogin):

        try:
            user = await UserRepository(self.session).get_filtered_by_params(
                email=user_data.email
            )

            prepared_user_data = UserInternal.model_validate(user[0])

            if not user or not verify_password(
                user_data.password, prepared_user_data.password
            ):
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Wrong user",
                )
            access_token = create_access_token(
                data={"user_id": str(prepared_user_data.id)}
            )
            refresh_token = create_refresh_token(
                data={"user_id": str(prepared_user_data.id)}
            )
            await TokenRepository(self.session).create(
                refresh_token=refresh_token, user_id=prepared_user_data.id
            )
            return {"access_token": access_token, "token_type": "bearer"}

        except IntegrityError as _ie:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f"Wrong data type, {_ie}",
            )

    async def user_logout(self, current_user_data: dict):
        try:
            user = await UserRepository(self.session).get_by_id(
                id=current_user_data["user"].id
            )
            tokens = await TokenRepository(self.session).get_filtered_by_params(
                user_id=user.id
            )
            if not tokens:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST, detail="Неверный токен"
                )
            await TokenRepository(self.session).delete_by_user_id(user_id=user.id)

            check_for_token = await TokenRepository(
                self.session
            ).get_filtered_by_params(user_id=user.id)
            if not check_for_token:
                return JSONResponse(
                    status_code=HTTP_204_NO_CONTENT, content={"detail": "Logout"}
                )

        except Exception as _e:
            raise HTTPException(status_code=400, detail=_e)

    async def get_current_user(self, current_user: dict):
        try:
            user_response = await UserRepository(self.session).get_by_id(
                id=current_user["user"].id
            )
            if not user_response:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST, detail="usr not found"
                )
            user = User.model_validate(user_response)
            return user
        except Exception as _e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(_e))

    async def update_current_user(self, current_user: dict, update_data: UserUpdate):
        try:
            if not update_data:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST, detail="wrong data"
                )
            cleaned_data = {
                k: v for k, v in update_data.model_dump().items() if v is not None
            }
            user = await UserRepository(self.session).update(
                id=current_user["user"].id, **cleaned_data
            )
            return User.model_validate(user)

        except Exception as _e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(_e))

    async def delete_current_user(
        self,
        current_user: dict,
    ):
        try:
            user = await UserRepository(self.session).get_by_id(
                id=current_user["user"].id
            )
            if not user:
                raise HTTPException(
                    status_code=HTTP_404_NOT_FOUND, detail="user not found"
                )
            await TokenRepository(self.session).delete_by_user_id(
                user_id=current_user["user"].id
            )
            await UserRepository(self.session).delete(id=current_user["user"].id)
            return JSONResponse(
                status_code=HTTP_204_NO_CONTENT, content="sucsessfully deleted"
            )
        except Exception as _e:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(_e))
