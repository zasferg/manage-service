import pytest
from app.infrastructure.services.companies import CompanyService
from app.infrastructure.repositories.company import CompanyRepository
from app.infrastructure.repositories.users import UserRepository


@pytest.mark.asyncio
async def test_create_company(test_session, test_company):

    await CompanyService(test_session).create_company(new_company=test_company)

    response = await CompanyRepository(test_session).get_filtered_by_params(
        name=test_company.name
    )

    assert response is not None


@pytest.mark.asyncio
async def test_add_user(test_session, test_company, test_user):
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
    response = await CompanyService(test_session).add_user_to_company(
        user_id=user_id, company_id=company_id
    )

    assert response.users[0].id == user_id
    assert response.id == company_id


@pytest.mark.asyncio
async def test_delete_user(test_session, test_company, test_user):
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
    await CompanyService(test_session).add_user_to_company(
        user_id=user_id, company_id=company_id
    )
    response = await CompanyService(test_session).delete_user_from_company(
        user_id=user_id, company_id=company_id
    )

    assert response.id == company_id
    assert response.users == []
