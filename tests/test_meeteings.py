from app.infrastructure.services.meetings import MeetingService
from app.infrastructure.schemas.schemas import MeetingCreate, MeetingWithRelations, User
from app.infrastructure.repositories.meetings import UserMeetingRepository
from app.infrastructure.repositories.users import UserRepository
from datetime import datetime, timedelta

import pytest


@pytest.mark.asyncio
async def test_create_meeting(test_session):
    await UserRepository(test_session).create(
        email="test_email1@mail.com",
        password="test_password1",
    )
    await UserRepository(test_session).create(
        email="test_email2@mail.com",
        password="test_password2",
    )

    users = await UserRepository(test_session).get_all(offset=0, limit=10)
    user_ids = [User.model_validate(user).id for user in users]
    meeting_data = MeetingCreate(
        description="test_descr",
        meeting_starttime=datetime.today() + timedelta(days=5),
        meeting_endtime=datetime.today() + timedelta(days=5, hours=2),
    )
    result, conflicts = await MeetingService(test_session).create_meeting(
        meeting=meeting_data, user_ids=user_ids
    )
    users_to_meeting = await UserMeetingRepository(test_session).get_filtered_by_params(
        meeting_id=result.id
    )
    assert conflicts is None
    assert result.description == meeting_data.description
    assert all(item in user_ids for item in users_to_meeting)


@pytest.mark.asyncio
async def test_get_meeting(test_session):
    await UserRepository(test_session).create(
        email="test_email1@mail.com",
        password="test_password1",
    )
    user = await UserRepository(test_session).get_filtered_by_params(
        email="test_email1@mail.com"
    )

    meeting_data_1 = MeetingCreate(
        description="test_descr1",
        meeting_starttime=datetime.today() + timedelta(days=5),
        meeting_endtime=datetime.today() + timedelta(days=5, hours=2),
    )
    meeting_data_2 = MeetingCreate(
        description="test_descr2",
        meeting_starttime=datetime.today() + timedelta(days=6),
        meeting_endtime=datetime.today() + timedelta(days=6, hours=2),
    )

    await MeetingService(test_session).create_meeting(
        meeting=meeting_data_1,
        user_ids=[
            user[0].id,
        ],
    )
    await MeetingService(test_session).create_meeting(
        meeting=meeting_data_2,
        user_ids=[
            user[0].id,
        ],
    )

    meetings = await MeetingService(test_session).get_meetings_for_user(
        user_id=user[0].id
    )

    assert len(meetings) == 2
    assert all(
        meeting.description in [meeting_data_1.description, meeting_data_2.description]
        for meeting in meetings
    )


@pytest.mark.asyncio
async def test_cancell_meeting(test_session):
    await UserRepository(test_session).create(
        email="test_email1@mail.com",
        password="test_password1",
    )
    user = await UserRepository(test_session).get_filtered_by_params(
        email="test_email1@mail.com"
    )

    meeting_data = MeetingCreate(
        description="test_descr",
        meeting_starttime=datetime.today() + timedelta(days=5),
        meeting_endtime=datetime.today() + timedelta(days=5, hours=2),
    )

    result, _ = await MeetingService(test_session).create_meeting(
        meeting=meeting_data,
        user_ids=[
            user[0].id,
        ],
    )

    result_cancelled = await MeetingService(test_session).cancel_meeting(
        meeting_id=result.id
    )

    assert result.id == result_cancelled.id
    assert result_cancelled.is_cancelled == True
