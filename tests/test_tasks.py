import pytest
from app.infrastructure.schemas.tasks import TaskCreate, TaskUpdate
from app.infrastructure.repositories.users import UserRepository
from app.infrastructure.repositories.company import CompanyRepository
from app.infrastructure.repositories.tasks import TaskRepository
from app.infrastructure.services.tasks import TaskService
from datetime import datetime, timedelta
from uuid import UUID


@pytest.mark.asyncio
async def test_create_task(
    test_session,
    test_user,
    test_company,
):

    await UserRepository(test_session).create(
        email=test_user.email, password=test_user.password
    )
    await CompanyRepository(test_session).create(name=test_company.name)
    user_id = await UserRepository(test_session).get_filtered_by_params(
        email=test_user.email
    )
    company_id = await CompanyRepository(test_session).get_filtered_by_params(
        name=test_company.name
    )

    task_schema = TaskCreate(
        description="test_descriiption",
        deadline=datetime.now() + timedelta(days=10),
        company_id=company_id[0].id,
        perform_user_id=user_id[0].id,
    )

    await TaskService(test_session).create_task(task_schema)

    task_from_db = await TaskRepository(test_session).get_filtered_by_params(
        description=task_schema.description
    )
    task_data = task_from_db[0]

    assert task_data.description == task_schema.description
    assert task_data.company_id == task_schema.company_id
    assert task_data.perform_user_id == task_schema.perform_user_id


@pytest.mark.asyncio
async def test_get_task(
    test_session,
    test_user,
    test_company,
):
    await UserRepository(test_session).create(
        email=test_user.email, password=test_user.password
    )
    await CompanyRepository(test_session).create(name=test_company.name)

    users = await UserRepository(test_session).get_filtered_by_params(
        email=test_user.email
    )
    companies = await CompanyRepository(test_session).get_filtered_by_params(
        name=test_company.name
    )

    user_id = users[0].id
    company_id = companies[0].id

    task_dict = {
        "id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b23"),
        "description": "test descr",
        "deadline": datetime.now() + timedelta(days=10),
        "company_id": company_id,
        "perform_user_id": user_id,
    }

    await TaskRepository(test_session).create(**task_dict)

    task_response = await TaskService(test_session).get_tasks_for_user(
        task_id=task_dict["id"], user_id=user_id
    )

    assert task_response.id == task_dict["id"]
    assert task_response.description == task_dict["description"]


@pytest.mark.asyncio
async def test_update_task(
    test_session,
    test_user,
    test_company,
):
    await UserRepository(test_session).create(
        email=test_user.email, password=test_user.password
    )
    await CompanyRepository(test_session).create(name=test_company.name)

    users = await UserRepository(test_session).get_filtered_by_params(
        email=test_user.email
    )
    companies = await CompanyRepository(test_session).get_filtered_by_params(
        name=test_company.name
    )
    user_id = users[0].id
    company_id = companies[0].id
    task_dict = {
        "id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b23"),
        "description": "test descr",
        "deadline": datetime.now() + timedelta(days=10),
        "company_id": company_id,
        "perform_user_id": user_id,
    }

    await TaskRepository(test_session).create(**task_dict)

    data_for_update = TaskUpdate(description="new_descr")
    await TaskService(test_session).update_task(
        task_id=task_dict["id"], data=data_for_update
    )

    updated_task_response = await TaskRepository(test_session).get_by_id(
        id=task_dict["id"]
    )

    assert updated_task_response.description == data_for_update.description


@pytest.mark.asyncio
async def test_delete_task(
    test_session,
    test_user,
    test_company,
):
    await UserRepository(test_session).create(
        email=test_user.email, password=test_user.password
    )
    await CompanyRepository(test_session).create(name=test_company.name)

    users = await UserRepository(test_session).get_filtered_by_params(
        email=test_user.email
    )
    companies = await CompanyRepository(test_session).get_filtered_by_params(
        name=test_company.name
    )

    user_id = users[0].id
    company_id = companies[0].id

    task_dict = {
        "id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b23"),
        "description": "test descr",
        "deadline": datetime.now() + timedelta(days=10),
        "company_id": company_id,
        "perform_user_id": user_id,
    }

    await TaskRepository(test_session).create(**task_dict)

    result = await TaskService(test_session).delete_task(task_id=task_dict["id"])
    get_none_result = await TaskRepository(test_session).get_by_id(id=task_dict["id"])
    assert result["status"] == 204
    assert result["detail"] == "Задача успешно удалена"
    assert get_none_result is None


@pytest.mark.asyncio
async def test_assign_to(
    test_session,
    test_user,
    test_company,
):
    await UserRepository(test_session).create(
        email=test_user.email, password=test_user.password
    )
    await CompanyRepository(test_session).create(name=test_company.name)

    users = await UserRepository(test_session).get_filtered_by_params(
        email=test_user.email
    )
    companies = await CompanyRepository(test_session).get_filtered_by_params(
        name=test_company.name
    )
    user_id = users[0].id
    company_id = companies[0].id

    task_dict = {
        "id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b23"),
        "description": "test descr",
        "deadline": datetime.now() + timedelta(days=10),
        "company_id": company_id,
        "perform_user_id": None,
    }

    await TaskRepository(test_session).create(**task_dict)

    result = await TaskService(test_session).assing_to(
        task_id=task_dict["id"],
        user_id=user_id,
    )

    assert result.id == task_dict["id"]
    assert result.perform_user_id == user_id


@pytest.mark.asyncio()
async def test_update_status(
    test_session,
    test_user,
    test_company,
):
    await CompanyRepository(test_session).create(name=test_company.name)

    companies = await CompanyRepository(test_session).get_filtered_by_params(
        name=test_company.name
    )
    company_id = companies[0].id

    task_dict = {
        "id": UUID("7193fb7d-5365-42ad-beaa-b935d77b1b23"),
        "description": "test descr",
        "deadline": datetime.now() + timedelta(days=10),
        "company_id": company_id,
        "perform_user_id": None,
    }

    await TaskRepository(test_session).create(**task_dict)

    from app.core.enums import TaskStatuses

    status = TaskStatuses.IN_PROGRESS

    result = await TaskService(test_session).assign_status(
        task_id=task_dict["id"], new_status=status
    )

    assert result.id == task_dict["id"]
    assert result.status == status
