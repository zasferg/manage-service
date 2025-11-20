from typing import Optional
from app.infrastructure.repositories.tasks import TaskRepository
from app.infrastructure.repositories.users import UserRepository
from app.infrastructure.repositories.comments import CommentsRepository
from app.infrastructure.schemas.tasks import TaskCreate, TaskGet
from app.infrastructure.schemas.comments import CommentCreate, CommentGet, CommentEntity
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.schemas.users import User
from uuid import UUID
from fastapi import status, HTTPException


class TaskService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task: TaskCreate, manager_id: UUID):
        new_task = await TaskRepository(self.session).create(
            description=task.description,
            deadline=task.deadline,
            company_id=task.company_id,
            perform_user_id=task.perform_user_id,
            author_id=manager_id,
        )
        return TaskGet.model_validate(new_task)

    async def get_tasks_for_user(self, task_id: UUID, user_id: UUID) -> TaskGet:
        tasks = await TaskRepository(self.session).get_filtered_by_params(
            id=task_id, perform_user_id=user_id
        )
        if not tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Нет задач для этого пользователя",
            )
        task_obj = tasks[0]
        return TaskGet.model_validate(task_obj)
    
    async def get_task(self, task_id: UUID):
        task = await TaskRepository(self.session).get_by_id(id=task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Нет задач для этого пользователя",
            )
        return TaskGet.model_validate(task)

    async def delete_task(self, task_id: UUID):
        result = await TaskRepository(self.session).delete(id=task_id)
        if result:
            response = {
                "status": status.HTTP_204_NO_CONTENT,
                "detail": "Задача успешно удалена",
            }
            return response
        return None

    async def assing_to(
        self, task_id: UUID, user_id: UUID, manager_id: UUID
    ) -> TaskGet:
        user_to_assign = await UserRepository(self.session).get_by_id(id=user_id)
        if not user_to_assign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не существует",
            )
        if user_to_assign and self._check_for_author(manager_id, task_id):
            updated_task = await TaskRepository(self.session).update(
                id=task_id, perform_user_id=user_id
            )
            return TaskGet.model_validate(updated_task)

    async def assign_status(self, task_id: UUID, new_status: str) -> TaskGet:
        updated_task = await TaskRepository(self.session).update(
            id=task_id, status=new_status
        )
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
            )
        return TaskGet.model_validate(updated_task)

    async def update_task(
        self, task_id: UUID, data: TaskCreate, manager_id: UUID
    ) -> TaskGet:
        cleaned_data = {k: v for k, v in data.model_dump().items() if v is not None}

        if cleaned_data and self._check_for_author(manager_id, task_id):
            updated_task = await TaskRepository(self.session).update(
                task_id, **cleaned_data
            )
            return TaskGet.model_validate(updated_task)

    async def create_comment(self, comment_data: CommentCreate) -> CommentGet:
        task = await TaskRepository(self.session).get_by_id(comment_data.task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Задача с ID {comment_data.task_id} не найдена",
            )
        from_user_obj = await UserRepository(self.session).get_by_id(
            id=comment_data.from_user_id
        )
        if not from_user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {comment_data.from_user_id} не найден",
            )
        to_user_obj = await UserRepository(self.session).get_by_id(
            comment_data.to_user_id
        )
        if not to_user_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {comment_data.from_user_id} не найден",
            )
        last_comment = await self._get_last_comment_in_chat(comment_data.task_id)

        prepared_comment_data = CommentEntity(
            task_id=comment_data.task_id,
            text=comment_data.text,
            from_user_id=comment_data.from_user_id,
            to_user_id=comment_data.to_user_id,
            parent_id=last_comment.id if last_comment else None,
        )
        try:
            comment = await CommentsRepository(self.session).create(
                task_id=prepared_comment_data.task_id,
                text=prepared_comment_data.text,
                from_user_id=prepared_comment_data.from_user_id,
                to_user_id=prepared_comment_data.to_user_id,
                parent_id=prepared_comment_data.parent_id,
            )
            return CommentGet.model_validate(comment)
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка при создании комментария: {str(e)}",
            )

    async def _get_last_comment_in_chat(self, task_id: UUID) -> Optional[CommentEntity]:
        all_comments = await CommentsRepository(self.session).get_filtered_by_params(
            task_id=task_id
        )
        if not all_comments:
            return None
        all_comments_prepared = [
            CommentGet.model_validate(comment) for comment in all_comments
        ]
        if all(comment.created for comment in all_comments_prepared):
            return max(all_comments_prepared, key=lambda x: x.created)

        return all_comments_prepared[-1]

    async def get_chat_history(
        self, task_id: UUID, user1: UUID, user2: UUID
    ) -> list[CommentGet]:
        all_comments = await CommentsRepository(self.session).get_filtered_by_params(
            task_id=task_id
        )
        if not all_comments:
            return None
        chat_comments = [
            comment
            for comment in all_comments
            if {comment.from_user_id, comment.to_user_id} == {user1, user2}
        ]

        if chat_comments and hasattr(chat_comments[0], "created"):
            chat_comments.sort(key=lambda x: x.created)
        else:
            chat_comments.sort(key=lambda x: x.id)
        return chat_comments

    async def _check_for_author(self, manager_id: UUID, task_id: UUID):
        task_for_update = TaskRepository(self.session).get_by_id(task_id)
        if not manager_id == task_for_update.author_id:
            return None
