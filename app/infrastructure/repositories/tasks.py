from infrastructure.repositories.base import BaseRepository
from infrastructure.database.models.models import Task
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select, func
from datetime import datetime


class TaskRepository(BaseRepository):

    def __init__(self, async_session: AsyncSession):
        super().__init__(Task, async_session)

    async def filter_by_period(self, start_date: datetime, to_date: datetime, **kwargs):
        stmt = (
            select(Task)
            .filter_by(**kwargs)
            .filter(Task.created.between(start_date, to_date))
        )
        result = await self.async_session.execute(stmt)
        return result.scalars().all()
