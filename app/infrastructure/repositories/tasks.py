from app.infrastructure.repositories.base import BaseRepository
from app.infrastructure.database.models.models import Task
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select, func
from datetime import date, datetime


class TaskRepository(BaseRepository):

    def __init__(self, async_session: AsyncSession):
        super().__init__(Task, async_session)

    async def filter_by_period(self, start_date: date, to_date: date, **kwargs):
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(to_date, datetime.max.time())
        stmt = (
            select(Task)
            .filter_by(**kwargs)
            .filter(Task.created.between(start_datetime, end_datetime))
        )
        result = await self.async_session.execute(stmt)
        return result.scalars().all()
