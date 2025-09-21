from infrastructure.repositories.calendar import CalendarRepository
from infrastructure.services.calendar import CalendarService
from core.permissions import user_manager_permission
from infrastructure.authentication.auth import access_token_auth
from infrastructure.schemas.schemas import *
from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.session import get_session


calendar = APIRouter(
    prefix="/calendar",
    tags=["Календарь"],
)


@calendar.get("/by_day")
async def get_events_by_day(
    year: int,
    month: int,
    day: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(access_token_auth),
):
    try:
        events = await CalendarRepository(session).get_day_events(
            year=year, month=month, day=day
        )
        if not events:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Нет событий"
            )
        csv_content = await CalendarService(session).convert_to_csv(events_data=events)
        if csv_content:
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=events_{year}_{month}.csv",
                    "Content-Type": "text/csv; charset=utf-8",
                },
            )
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))


@calendar.get("/by_month")
async def get_events_by_month_by_csv(
    year: int,
    month: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(access_token_auth),
):
    try:
        events = await CalendarRepository(session).get_month_events(
            year=year,
            month=month,
        )
        if not events:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Нет событий"
            )
        csv_content = await CalendarService(session).convert_to_csv(events_data=events)
        if csv_content:
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=events_{year}_{month}.csv",
                    "Content-Type": "text/csv; charset=utf-8",
                },
            )

    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))
