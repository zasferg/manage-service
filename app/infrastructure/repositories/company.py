from app.infrastructure.repositories.base import BaseRepository
from app.infrastructure.database.models.models import Company
from sqlalchemy.ext.asyncio import AsyncSession


class CompanyRepository(BaseRepository):

    def __init__(self, async_session: AsyncSession):
        super().__init__(Company, async_session)
