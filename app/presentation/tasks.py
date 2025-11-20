from app.infrastructure.services.tasks import TaskService
from app.core.enums import TaskStatuses
from app.core.permissions import user_manager_permission
from app.infrastructure.authentication.auth import access_token_auth
from app.infrastructure.schemas.comments import CommentCreate, CommentGet
from app.infrastructure.schemas.tasks import TaskGet, TaskCreate, TaskUpdate
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_session
from uuid import UUID
from pydantic import Field


tasks = APIRouter(
    prefix="/tasks",
    tags=[
        "Задания",
    ],
)


@tasks.get("/task")
async def get_task(
    task_id: UUID,
    current_user=Depends(access_token_auth),
    session: AsyncSession = Depends(get_session),
) -> TaskGet:
    try:
        tasks = await TaskService(session).get_tasks_for_user(
            task_id=task_id, user_id=current_user["user"].id
        )
        return tasks
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))


@tasks.post("/task")
async def create_task(
    new_task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    manager_permission=Depends(user_manager_permission),
) -> TaskGet:
    try:
        if not manager_permission.company_id == new_task_data.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Данный менеджер не привязан к этой компании",
            )
        if new_task_data:
            new_task = await TaskService(session).create_task(
                task=new_task_data, manager_id=manager_permission.id
            )
            if new_task:
                return new_task
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))


@tasks.put("/task")
async def update_task(
    task_id: UUID,
    new_task_data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    manager_permission=Depends(user_manager_permission),
) -> TaskGet:
    try:
        if not manager_permission.company_id == new_task_data.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Данный менеджер не привязан к этой компании",
            )
        if new_task_data:
            new_task = await TaskService(session).update_task(
                task_id=task_id, manager_id=manager_permission.id, data=new_task_data
            )
            if new_task:
                return new_task
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))


@tasks.delete("/task")
async def delete_task(
    task_id: UUID,
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
    manager_permission=Depends(user_manager_permission),
) -> TaskGet:
    try:
        task = TaskService(session).get_task(task_id=task_id)
        if not manager_permission.company_id == task.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Данный менеджер не привязан к этой компании",
            )
        result = TaskService(session).delete_task(
            task_id=task_id, manager_id=manager_permission.id
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Задания не найдено"
            )
        return result
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))
    except ValueError as _ve:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(_ve))


@tasks.put("/update_status")
async def update_status(
    task_id: UUID,
    new_status: str = Field,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(access_token_auth),
) -> TaskGet:
    try:
        task = await TaskService(session).get_tasks_for_user(user_id=current_user["user"].id, task_id=task_id)
        if not current_user["user"].company_id == task.company_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Данный пользователь не имеет такого задания",
            )
        if not TaskStatuses.check_for_value(new_status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Неправильный статус"
            )
        updated_status_task = await TaskService(session).assign_status(
            task_id=task_id, new_status=new_status
        )
        if not updated_status_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
            )
        return updated_status_task
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))


@tasks.post("/assign_to")
async def assign_task_to(
    user_id: UUID,
    task_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_permission=Depends(user_manager_permission),
):
    try:
        updated_task = await TaskService(session).assing_to(
            user_id=user_id, task_id=task_id, manager_id=user_permission.id
        )
        return updated_task
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))
    except ValueError as _ve:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(_ve))


@tasks.post("/create_comment")
async def create_comment(
    comment_data: CommentCreate,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(access_token_auth),
) -> CommentGet:
    try:
        comment_data.from_user_id = current_user["user"].id
        new_comment = await TaskService(session).create_comment(comment_data)
        if new_comment:
            return new_comment
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))
    except ValueError as _ve:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(_ve))


@tasks.get("/chat_history")
async def get_chat_history(
    task_id: UUID,
    user1: UUID,
    user2: UUID,
    session: AsyncSession = Depends(get_session),
) -> list[CommentGet]:
    try:
        chat_history = await TaskService(session).get_chat_history(
            task_id=task_id, user1=user1, user2=user2
        )
        if not chat_history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="История пуста"
            )
        return chat_history
    except Exception as _e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(_e))
    except ValueError as _ve:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(_ve))
