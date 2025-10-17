from app.infrastructure.repositories.base import BaseRepository
from app.infrastructure.database.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepository):

    def __init__(self, async_session: AsyncSession):
        super().__init__(User, async_session)
