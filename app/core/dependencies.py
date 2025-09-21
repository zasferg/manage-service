from infrastructure.repositories.calendar import CalendarRepository
from infrastructure.services.companies import CompanyService
from infrastructure.services.tasks import TaskService
from infrastructure.services.meetings import MeetingService
from infrastructure.database.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated

AsyncSessionType = Annotated[AsyncSession, Depends(get_session)]
