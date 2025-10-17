from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generator

engine = create_async_engine(url=settings.postgres_db_url())

async_session = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


async def get_session() -> Generator:
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
