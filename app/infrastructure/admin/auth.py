from sqladmin.authentication import AuthenticationBackend
from fastapi import Request
from app.core.auth import verify_password
from app.infrastructure.database.session import async_session
from app.infrastructure.repositories.users import UserRepository
from app.core.enums import RolesEnum
from app.core.log import setup_logger

logger = setup_logger()


class DBAuth(AuthenticationBackend):
    async def login(
        self,
        request: Request,
    ) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")
        async with async_session() as db_session:
            users = await UserRepository(db_session).get_filtered_by_params(email=email)
            if users:
                user = users[0]
                if (
                    user
                    and verify_password(password, user.password)
                    and user.role == RolesEnum.ADMIN
                ):
                    request.session.update(
                        {"user_id": str(user.id), "role": RolesEnum.ADMIN}
                    )
                    return True
            logger.error(f"Ошибка при логине пользователя {email}")
            return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_role = request.session.get("role")
        if user_role == RolesEnum.ADMIN:
            return True
        logger.error(user_role)
        return False
