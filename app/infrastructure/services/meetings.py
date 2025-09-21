from infrastructure.schemas.schemas import *
from infrastructure.repositories.meetings import (
    MeetingRepository,
    UserMeetingRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from uuid import UUID
from sqlalchemy import select, and_


class MeetingService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_meeting(
        self, meeting: MeetingCreate, user_ids: list[UUID]
    ) -> Meeting:
        try:
            new_meeting = await MeetingRepository(self.session).create(**meeting.model_dump())
            if new_meeting:
                meeting, conflicts = await self.add_users_to_meeting(
                    meeting_id=new_meeting.id, user_ids=user_ids
                )
                return meeting, conflicts
        except Exception as e:
                await MeetingRepository(self.session).delete(id=new_meeting.id)
                raise HTTPException(
                    status_code=400,
                    detail=str(e)
                )

    async def add_users_to_meeting(self, meeting_id: UUID, user_ids: list[UUID]):

        meeting = await MeetingRepository(self.session).get_by_id(meeting_id)
        if meeting:
            conflicts = await self._check_user_meeting_conflicts(
                user_ids=user_ids,
                meeting_start=meeting.meeting_starttime,
                meeting_end=meeting.meeting_endtime,
                exclude_meeting_id=meeting_id,
            )
            valid_user_ids = [
                user_id for user_id in user_ids if user_id not in conflicts
            ]

            if not valid_user_ids:
                raise ValueError(
                    f"Все пользователи имеют временные конфликты: {conflicts}"
                )

            objects = [
                UserMeetingRelationCreate(user_id=item, meeting_id=meeting_id).model_dump()
                for item in user_ids
            ]

            result = await UserMeetingRepository(self.session).bulk_create(objects)

            conflict_response = (
                f"Пропущено {len(conflicts)} пользователей из-за конфликтов"
            )

        if result:
            updated_meeting = await MeetingRepository(self.session).get_by_id(
                id=meeting_id
            )
            return updated_meeting, conflict_response if conflicts else None

    async def get_meetings_for_user(self, user_id: UUID) -> list[Meeting]:

        meetings = await UserMeetingRepository(self.session).get_user_meetings(user_id)
        if meetings:
            return [Meeting.model_validate(meeting) for meeting in meetings]

    async def cancel_meeting(self, meeting_id: UUID):

        updated_meeting = await MeetingRepository(self.session).update(
            id=meeting_id, is_cancelled=True
        )

        if updated_meeting:
            return updated_meeting

    async def _check_user_meeting_conflicts(
        self,
        user_ids: List[UUID],
        meeting_start: datetime,
        meeting_end: datetime,
        exclude_meeting_id: Optional[UUID] = None,
    ) -> dict:

        from infrastructure.database.models.models import (
            UserMeetingRelation,
            Meetings,
        )

        conflicts = {}

        for user_id in user_ids:
            query = (
                select(Meetings)
                .join(
                    UserMeetingRelation, Meetings.id == UserMeetingRelation.c.meeting_id
                )
                .where(
                    and_(
                        UserMeetingRelation.c.user_id == user_id,
                        Meetings.meeting_starttime < meeting_end,
                        Meetings.meeting_endtime > meeting_start,
                        (
                            Meetings.id != exclude_meeting_id
                            if exclude_meeting_id
                            else True
                        ),
                    )
                )
            )

            result = await self.session.execute(query)
            conflicting_meetings = result.scalars().all()

            if conflicting_meetings:
                conflicts[user_id] = [
                    {
                        "conflicting_meeting_id": meeting.id,
                        "conflicting_start": meeting.meeting_starttime,
                        "conflicting_end": meeting.meeting_endtime,
                        "conflicting_description": getattr(
                            meeting, "description", "Неизвестная встреча"
                        ),
                    }
                    for meeting in conflicting_meetings
                ]

        return conflicts
