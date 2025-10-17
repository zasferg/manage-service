from app.infrastructure.repositories.base import BaseRepository
from app.infrastructure.database.models.models import Comments
from sqlalchemy.ext.asyncio import AsyncSession


class CommentsRepository(BaseRepository):

    def __init__(self, async_session: AsyncSession):
        super().__init__(Comments, async_session)
