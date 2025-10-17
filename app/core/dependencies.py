from app.infrastructure.repositories.calendar import CalendarRepository
from app.infrastructure.services.companies import CompanyService
from app.infrastructure.services.tasks import TaskService
from app.infrastructure.services.meetings import MeetingService
from app.infrastructure.database.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated

AsyncSessionType = Annotated[AsyncSession, Depends(get_session)]
