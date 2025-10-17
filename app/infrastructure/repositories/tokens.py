from app.infrastructure.repositories.base import BaseRepository
from app.infrastructure.database.models.models import Token
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import delete


class TokenRepository(BaseRepository):

    def __init__(self, async_session: AsyncSession):
        super().__init__(Token, async_session)

    async def delete_by_user_id(self, user_id: UUID) -> int:
        stmt = delete(self.model).where(self.model.user_id == user_id)
        result = await self.async_session.execute(stmt)
        return result.rowcount
