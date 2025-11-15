from app.infrastructure.services.meetings import MeetingService
from app.infrastructure.database.session import get_session
from app.infrastructure.authentication.auth import access_token_auth
from app.infrastructure.schemas.meetings import Meeting, MeetingCreate
from app.core.permissions import user_manager_permission
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID


meetings = APIRouter(
    prefix="/meetings",
    tags=[
        "Встречи",
    ],
)


@meetings.get("")
async def get_meetings(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(access_token_auth),
) -> list[Meeting]:
    try:
        meetings = await MeetingService(session).get_meetings_for_user(
            user_id=current_user["user"].id
        )
        return meetings
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))


@meetings.post("")
async def create_meeting(
    user_ids: list[UUID],
    meeting_data: MeetingCreate,
    session: AsyncSession = Depends(get_session),
    manager_permission=Depends(user_manager_permission),
):
    try:
        new_meeting, conflicts = await MeetingService(session).create_meeting(
            user_ids=user_ids, meeting=meeting_data
        )
        if new_meeting:
            response = {
                "status": status.HTTP_201_CREATED,
                "meeting": new_meeting,
                "conflicts": conflicts,
            }
            return response
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))


@meetings.put("/cancel")
async def cancel_meeting(
    meeting_id: UUID,
    session: AsyncSession = Depends(get_session),
    manager_permssion=Depends(user_manager_permission),
):
    try:
        result = await MeetingService(session).cancel_meeting(meeting_id=meeting_id)
        if result:
            response = {
                "status": status.HTTP_200_OK,
                "details": f"Встреча id{meeting_id} отменена",
            }
            return response
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))
