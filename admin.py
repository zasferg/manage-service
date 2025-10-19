from app.core.auth import hash_password
from app.core.enums import RolesEnum
from app.core.log import setup_logger
from app.infrastructure.repositories.users import UserRepository

import asyncio
import getpass

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://username:password@localhost:5434/local_db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

logger = setup_logger()


async def create_admin():
    logger.info("=== Начало создания администратора ===")
    while True:
        admin_email = input("Введите email администратора: ").strip()
        if "@" in admin_email and "." in admin_email:
            break
        logger.error("Введен некорректный email адрес")

    while True:
        admin_password = getpass.getpass("Введите пароль администратора: ").strip()
        admin_password_confirm = getpass.getpass("Подтвердите пароль: ").strip()

        if admin_password == admin_password_confirm:
            if len(admin_password) >= 5:
                break
            else:
                logger.warning("Пароль должен содержать минимум 5 символов")
        else:
            logger.error("Пароли не совпадают")

    logger.info(f"Попытка создания пользователя с email: {admin_email}")

    try:
        async with async_session() as session:
            user = await UserRepository(session).create(
                email=admin_email,
                password=hash_password(admin_password),
                role=RolesEnum.ADMIN,
            )
            logger.info("Администратор успешно создан!")
            logger.info(
                f"Создан пользователь: ID={user.id}, Email={user.email}, Role={user.role}"
            )
            return user
    except Exception as e:
        logger.error(f"Ошибка при создании администратора: {e}", exc_info=True)
        return None


async def main():
    try:
        await create_admin()
    except KeyboardInterrupt:
        logger.info("Создание администратора прервано пользователем")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
