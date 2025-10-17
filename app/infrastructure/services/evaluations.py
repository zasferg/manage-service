from app.infrastructure.repositories.evaluations import EvalustionsRepository
from app.infrastructure.repositories.tasks import TaskRepository
from app.infrastructure.schemas.evaluations import EvaluationCreate, EvaluationGet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import date
import statistics


class EvaluationService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_rating(self, payload: EvaluationCreate) -> EvaluationGet:
        task = await TaskRepository(self.session).get_by_id(id=payload.task_id)
        if not task:
            raise ValueError(f"ЗАдание с id {payload.task_id} не найдено")
        evaluation_check = await EvalustionsRepository(
            self.session
        ).get_filtered_by_params(task_id=task.id)
        if evaluation_check:
            raise ValueError(
                f"Задание с id {payload.task_id} уже имеет оценку{evaluation_check[0].mark}"
            )
        new_evaluation = await EvalustionsRepository(self.session).create(
            task_id=payload.task_id, mark=payload.mark
        )
        if new_evaluation:
            return EvaluationGet.model_validate(new_evaluation)

    async def get_ratings(self, user_id: UUID) -> list:

        tasks = await TaskRepository(self.session).get_filtered_by_params(
            perform_user_id=user_id
        )
        if not tasks:
            raise ValueError(f"Заданий не найдено")
        task_ids = [task.id for task in tasks]
        evaluations = await EvalustionsRepository(self.session).get_bulk_evaluations(
            task_ids=task_ids
        )
        if not evaluations:
            raise ValueError(f"Оценок не найдено")

        return [EvaluationGet.model_validate(evaluation) for evaluation in evaluations]

    async def get_avg_rating(
        self, user_id: UUID, from_date: date, to_date: date
    ) -> int:
        tasks = await TaskRepository(self.session).filter_by_period(
            start_date=from_date, to_date=to_date, perform_user_id=user_id
        )
        if not tasks:
            raise ValueError(f"Заданий не найдено")
        task_ids = [task.id for task in tasks]
        evaluations = await EvalustionsRepository(self.session).get_bulk_evaluations(
            task_ids=task_ids
        )
        if not evaluations:
            raise ValueError(f"Оценок не найдено")

        evaluations_marks = [evaluation.mark for evaluation in evaluations]
        avg = statistics.mean(evaluations_marks)

        return float(avg)
