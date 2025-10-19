from app.infrastructure.repositories.base import BaseRepository
from app.infrastructure.database.models.models import Evaluation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class EvaluationsRepository(BaseRepository):

    def __init__(self, async_session: AsyncSession):
        super().__init__(Evaluation, async_session)

    async def get_bulk_evaluations(self, task_ids: list):
        stmt = select(Evaluation).where(Evaluation.task_id.in_(task_ids))
        objects = await self.async_session.execute(stmt)
        return objects.scalars().all()
