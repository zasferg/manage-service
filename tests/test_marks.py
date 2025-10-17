import pytest
from app.infrastructure.services.evaluations import EvaluationService
from app.infrastructure.repositories.evaluations import EvalustionsRepository
from app.infrastructure.repositories.tasks import TaskRepository
from uuid import UUID
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_add_rating(test_session, make_user_and_company):
    user_id, company_id = make_user_and_company
    expected_rating = 4
    task_dict = {
        "id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b23"),
        "description": "test descr",
        "deadline": datetime.now() + timedelta(days=10),
        "company_id": company_id,
        "perform_user_id": user_id,
    }

    await TaskRepository(test_session).create(**task_dict)

    result = await EvaluationService(test_session).add_rating(
        task_id=task_dict["id"], mark=expected_rating
    )

    assert result.task_id == task_dict["id"]
    assert result.mark == expected_rating


@pytest.mark.asyncio
async def test_get_all_ratings(test_session, make_user_and_company):
    user_id, company_id = make_user_and_company

    task_list = [
        {
            "id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b23"),
            "description": "test descr",
            "deadline": datetime.now() + timedelta(days=10),
            "company_id": company_id,
            "perform_user_id": user_id,
            "mark": 4,
        },
        {
            "id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b24"),
            "description": "test descr 2",
            "deadline": datetime.now() + timedelta(days=5),
            "company_id": company_id,
            "perform_user_id": user_id,
            "mark": 3,
        },
        {
            "id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b25"),
            "description": "test descr 3",
            "deadline": datetime.now() + timedelta(days=15),
            "company_id": company_id,
            "perform_user_id": user_id,
            "mark": 2,
        },
    ]
    marks_list = [
        {
            "task_id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b23"),
            "mark": 4,
        },
        {
            "task_id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b24"),
            "mark": 3,
        },
        {
            "task_id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b25"),
            "mark": 2,
        },
    ]

    for task in task_list:
        await TaskRepository(test_session).create(**task)

    for mark in marks_list:
        await EvalustionsRepository(test_session).create(**mark)

    result = await EvaluationService(test_session).get_ratings(user_id=user_id)

    assert len(result) == 3
    assert result[0]["id"] == task_list[0]["id"]
    assert result[0]["mark"] == 4
    assert result[1]["id"] == task_list[1]["id"]
    assert result[1]["mark"] == 3
    assert result[2]["id"] == task_list[2]["id"]
    assert result[2]["mark"] == 2


@pytest.mark.asyncio
async def test_get_avg_rating(test_session, make_user_and_company):
    user_id, company_id = make_user_and_company

    task_list = [
        {
            "id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b23"),
            "description": "test descr",
            "deadline": datetime.now() + timedelta(days=10),
            "company_id": company_id,
            "perform_user_id": user_id,
            "mark": 4,
        },
        {
            "id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b24"),
            "description": "test descr 2",
            "deadline": datetime.now() + timedelta(days=5),
            "company_id": company_id,
            "perform_user_id": user_id,
            "mark": 3,
        },
        {
            "id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b25"),
            "description": "test descr 3",
            "deadline": datetime.now() + timedelta(days=15),
            "company_id": company_id,
            "perform_user_id": user_id,
            "mark": 2,
        },
    ]
    marks_list = [
        {
            "task_id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b23"),
            "mark": 4,
        },
        {
            "task_id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b24"),
            "mark": 3,
        },
        {
            "task_id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b25"),
            "mark": 2,
        },
    ]

    for task in task_list:
        await TaskRepository(test_session).create(**task)

    for mark in marks_list:
        await EvalustionsRepository(test_session).create(**mark)

    result = await EvaluationService(test_session).get_avg_rating(
        user_id=user_id,
        from_date=datetime.today() - timedelta(days=2),
        to_date=datetime.today(),
    )

    assert result == 3
