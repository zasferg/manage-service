from app.infrastructure.services.evaluations import EvaluationService
from app.core.permissions import user_manager_permission
from app.infrastructure.authentication.auth import access_token_auth
from app.infrastructure.schemas.evaluations import EvaluationCreate, EvaluationGet
from app.infrastructure.database.session import get_session
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

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
        ratings = await EvaluationService(session).get_ratings(
            user_id=current_user["user"].id
        )
        if ratings:
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
        avg_rating = await EvaluationService(session).get_avg_rating(
            user_id=current_user["user"].id,
            from_date=from_date,
            to_date=to_date,
        )
        if avg_rating:
            response = {"avg_rating": avg_rating}
            return response
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))


@marks.post("/add_rating")
async def add_rating(
    payload: EvaluationCreate,
    session: AsyncSession = Depends(get_session),
    manager_permisisons=Depends(user_manager_permission),
) -> EvaluationGet:
    try:
        task = await EvaluationService(session).add_rating(payload=payload)
        if task:
            return task
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))
