from infrastructure.repositories.base import BaseRepository
from infrastructure.database.models.models import Meetings, UserMeetingRelation
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from uuid import UUID


class MeetingRepository(BaseRepository):

    def __init__(self, async_session: AsyncSession):
        super().__init__(Meetings, async_session)


class UserMeetingRepository(BaseRepository):

    def __init__(self, async_session: AsyncSession):
        super().__init__(UserMeetingRelation, async_session)

    async def bulk_create(self, entities):
        try:
            stmt = insert(self.model).values(entities)
            await self.async_session.execute(stmt)
            await self.async_session.commit()
            return True
        except Exception as e:
            await self.async_session.rollback()
            raise e

    async def get_user_meetings(self, user_id: UUID):
        query = (
            select(Meetings)
            .join(UserMeetingRelation, Meetings.id == UserMeetingRelation.c.meeting_id)
            .where(UserMeetingRelation.c.user_id == user_id)
            .order_by(Meetings.meeting_starttime.desc())
        )

        result = await self.async_session.execute(query)
        meetings = result.scalars().all()

        return meetings
