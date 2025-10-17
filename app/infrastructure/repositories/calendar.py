from app.infrastructure.repositories.base import BaseRepository
from app.infrastructure.database.models.models import Task, Meetings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, union_all, extract, literal


class CalendarRepository(BaseRepository):

    def __init__(self, async_session: AsyncSession):
        self.session = async_session

    async def get_month_events(self, year: int, month: int):

        stmt_task = select(
            Task.id,
            Task.description,
            Task.deadline.label("date_field"),
            literal("task").label("type"),
        ).where(
            extract("year", Task.deadline) == year,
            extract("month", Task.deadline) == month,
        )

        stmt_meetings = select(
            Meetings.id,
            Meetings.description,
            Meetings.meeting_starttime.label("date_field"),
            literal("meeting").label("type"),
        ).where(
            extract("year", Meetings.meeting_starttime) == year,
            extract("month", Meetings.meeting_starttime) == month,
        )

        union_stmt = union_all(stmt_task, stmt_meetings).order_by("date_field")

        async with self.session as session:
            result = await session.execute(union_stmt)
            return result.all()

    async def get_day_events(self, year: int, month: int, day: int):

        stmt_meetings = select(
            Meetings.id,
            Meetings.description,
            Meetings.meeting_starttime.label("date_field"),
            literal("meeting").label("type"),
        ).where(
            extract("year", Meetings.meeting_starttime) == year,
            extract("month", Meetings.meeting_starttime) == month,
            extract("day", Meetings.meeting_starttime) == day,
        )

        stmt_task = select(
            Task.id,
            Task.description,
            Task.deadline.label("date_field"),
            literal("task").label("type"),
        ).where(
            extract("year", Task.deadline) == year,
            extract("month", Task.deadline) == month,
            extract("day", Task.deadline) == day,
        )

        union_stmt = union_all(stmt_task, stmt_meetings).order_by("date_field")

        async with self.session as session:
            result = await session.execute(union_stmt)
            return result.all()
