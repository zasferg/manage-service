from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from pydantic import computed_field
import os

# Определяем путь к .env файлу (в корне проекта)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=ENV_PATH)

    DEBUG: bool = True

    TEST_DB_NAME: str
    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASSWORD: str

    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str

    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int
    VERIFICATION_CODE_EXPIRE_SECONDS: int

    SECRET_KEY_FOR_ADMIN: str

    def postgres_db_url(self) -> str:
        if self.DEBUG:
            return f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASSWORD}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
        else:
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()

print(settings.postgres_db_url())
