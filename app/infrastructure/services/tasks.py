from infrastructure.repositories.tasks import TaskRepository
from infrastructure.repositories.users import UserRepository
from infrastructure.repositories.comments import CommentsRepository
from infrastructure.repositories.calendar import CalendarRepository
from infrastructure.schemas.schemas import *
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from core.enums import RolesEnum, TaskStatuses, Events
from fastapi import status, HTTPException


class TaskService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task: TaskCreate):
        new_task = await TaskRepository(self.session).create(
            description=task.description,
            deadline=task.deadline,
            company_id=task.company_id,
            perform_user_id=task.perform_user_id,
        )
        return TaskGet.model_validate(new_task)

    async def get_task(self, task_id: UUID, user_id: UUID) -> TaskGet:
        tasks = await TaskRepository(self.session).get_filtered_by_params(
            perform_user_id=user_id
        )

        task_prepared = [TaskGet.model_validate(obj).id for obj in tasks]
        if not tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Нет задач для этого пользователя",
            )
        if not task_id in task_prepared:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Данной задачи нет у пользователя",
            )
        task = await TaskRepository(self.session).get_by_id(id=task_id)
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

    async def assing_to(self, task_id: UUID, user_id: UUID) -> TaskGet:
        user_to_assign = await UserRepository(self.session).get_by_id(id=user_id)
        if not user_to_assign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не существует",
            )
        if user_to_assign:
            updated_task = await TaskRepository(self.session).update(
                id=task_id, perform_user_id=user_id
            )
            return TaskGet.model_validate(updated_task)

    async def assign_status(self, task_id: UUID, new_status: str) -> TaskGet:
        updated_task = await TaskRepository(self.session).update(
            id=task_id, status=new_status
        )
        return TaskGet.model_validate(updated_task)

    async def update_task(self, task_id: UUID, data: TaskCreate) -> TaskGet:
        cleaned_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if cleaned_data:
            updated_task = await TaskRepository(self.session).update(
                task_id, **cleaned_data
            )
            return TaskGet.model_validate(updated_task)

    async def add_rating(self, task_id: UUID, rating: RatingRequest) -> TaskGet:
        updated_task = await TaskRepository(self.session).update(
            id=task_id, mark=rating.rating
        )
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Не найдено оценок"
            )
        return TaskGet.model_validate(updated_task)

    async def get_ratings(self, user_id: UUID) -> list:
        tasks = await TaskRepository(self.session).get_filtered_by_params(
            perform_user_id=user_id
        )
        if not tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Не найдено оценок"
            )
        return [
            TaskGet.model_validate(task).model_dump(
                include=["id", "description", "mark"]
            )
            for task in tasks
        ]

    async def get_avg_rating(
        self, user_id: UUID, from_date: datetime, to_date: datetime
    ) -> int:
        tasks = await TaskRepository(self.session).filter_by_period(
            start_date=from_date, to_date=to_date, perform_user_id=user_id
        )
        task_marks = [task.mark for task in tasks]

        import statistics

        avg = statistics.mean(task_marks)

        return float(avg)

    async def create_comment(self, comment_data: CommentCreate) -> CommentGet:
        task = await TaskRepository(self.session).get_by_id(comment_data.task_id)
        if not task:
            raise ValueError(f"Задача с ID {comment_data.task_id} не найдена")
        from_user_obj = await UserRepository(self.session).get_by_id(
            id=comment_data.from_user_id
        )
        if not from_user_obj:
            raise ValueError(f"Пользователь с ID {comment_data.from_user_id} не найден")
        to_user_obj = await UserRepository(self.session).get_by_id(
            comment_data.to_user_id
        )
        if not to_user_obj:
            raise ValueError(f"Пользователь с ID {comment_data.to_user_id} не найден")
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
            raise Exception(f"Ошибка при создании комментария: {str(e)}")

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
