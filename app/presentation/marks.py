from infrastructure.services.tasks import TaskService
from infrastructure.repositories.tasks import TaskRepository
from core.permissions import user_manager_permission
from infrastructure.authentication.auth import access_token_auth
from infrastructure.schemas.schemas import *
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.session import get_session

marks = APIRouter(
    prefix="/marks",
    tags=[
        "Оценки",
    ],
)


@marks.get("/get_marks")
async def get_marks_for_user(
    current_user=Depends(access_token_auth),
    session: AsyncSession = Depends(get_session),
):
    try:
        ratings = await TaskService(session).get_ratings(
            user_id=current_user["user"].id
        )
        return ratings
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))


@marks.get("/get_avg_marks")
async def get_avg_marks_for_user(
    from_date: datetime,
    to_date: datetime,
    current_user=Depends(access_token_auth),
    session: AsyncSession = Depends(get_session),
) -> dict:
    try:
        avg_rating = await TaskService(session).get_avg_rating(
            user_id=current_user["user"].id,
            from_date=from_date,
            to_date=to_date,
        )
        if not avg_rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Не найдено оценок"
            )
        response = {"avg_rating": avg_rating}
        return response
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))


@marks.put("/add_rating")
async def add_rating(
    task_id: UUID,
    rating: RatingRequest,
    session: AsyncSession = Depends(get_session),
    manager_permisisons=Depends(user_manager_permission),
) -> TaskGet:
    try:
        task = await TaskService(session).add_rating(
            task_id=task_id,
            rating=rating,
        )
        return task
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))
