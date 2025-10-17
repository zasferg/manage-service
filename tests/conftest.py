import asyncio
from app.infrastructure.schemas.users import UserCreate
from app.infrastructure.database.models.models import *
from app.infrastructure.repositories.users import UserRepository
from app.infrastructure.repositories.company import CompanyRepository
import pytest, pytest_asyncio
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True, scope="function")
async def create_db_tables():
    if not settings.DEBUG:
        raise "Not test enviroment"

    engine = create_async_engine(url=settings.postgres_db_url(), pool_pre_ping=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="function")
async def test_session(create_db_tables):
    engine = create_async_engine(url=settings.postgres_db_url(), pool_pre_ping=True)
    async_session = async_sessionmaker(
        bind=engine, autocommit=False, autoflush=False, class_=AsyncSession
    )

    async with async_session() as session:
        yield session


@pytest.fixture
def test_user():
    user = UserCreate(email="test@email.com", password="12345")
    return user


@pytest.fixture()
def test_company():
    company = Company(name="test_company")
    return company


@pytest_asyncio.fixture
async def make_user_and_company(
    test_session,
    test_user,
    test_company,
):
    await UserRepository(test_session).create(
        email=test_user.email, password=test_user.password
    )
    await CompanyRepository(test_session).create(name=test_company.name)

    users = await UserRepository(test_session).get_filtered_by_params(
        email=test_user.email
    )
    companies = await CompanyRepository(test_session).get_filtered_by_params(
        name=test_company.name
    )

    user_id = users[0].id
    company_id = companies[0].id

    return user_id, company_id
