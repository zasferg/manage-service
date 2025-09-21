from infrastructure.repositories.company import CompanyRepository
from infrastructure.repositories.users import UserRepository
from infrastructure.schemas.schemas import CompanyCreate, Company, User
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from core.enums import RolesEnum


class CompanyService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_company(self, id: int) -> Company:
        company = await CompanyRepository(self.session).get_by_id(id=id)
        return Company.model_validate(company)

    async def create_company(self, new_company: CompanyCreate) -> Company:
        if new_company:
            new_company = await CompanyRepository(self.session).create(
                name=new_company.name
            )
            return Company.model_validate(new_company)
        else:
            raise Exception

    async def add_user_to_company(self, company_id: UUID, user_id: UUID) -> Company:
        check_for_company = await CompanyRepository(self.session).get_by_id(company_id)
        if check_for_company:
            await UserRepository(self.session).update(id=user_id, company_id=company_id)
            updated_company = await CompanyRepository(self.session).get_by_id(
                company_id
            )
            return Company.model_validate(updated_company)

    async def delete_user_from_company(self, user_id: UUID, company_id: UUID):
        users = await self.get_company_users(company_id=company_id)
        for user in users:
            await UserRepository(self.session).update(id=user.id, company_id=None)
            updated_company = await CompanyRepository(self.session).get_by_id(
                id=company_id
            )
            return Company.model_validate(updated_company)

    async def get_company_users(
        self,
        company_id: UUID,
    ):

        users_for_company = await UserRepository(self.session).get_filtered_by_params(
            company_id=company_id,
        )
        return [User.model_validate(obj) for obj in users_for_company]

    async def assign_comppany_role(
        self, company_id: UUID, user_id: UUID, user_role: RolesEnum
    ) -> User:
        company_user_ids = await self.get_company_users(company=company_id)
        if user_id in company_user_ids:
            updated_user = await UserRepository(self.session).update(
                user_id, role=user_role
            )
            return User.model_validate(updated_user)
