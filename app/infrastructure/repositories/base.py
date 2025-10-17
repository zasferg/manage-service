from app.infrastructure.database.session import get_session
from sqlalchemy import select, update, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import TypeVar

Model = TypeVar("Model", bound=declarative_base())


class BaseRepository:

    def __init__(self, model: Model, async_session: AsyncSession):
        self.model = model
        self.async_session = async_session

    async def get_all(self, offset: int, limit: int) -> list:
        stmt = select(self.model).offset(offset).limit(limit)
        response = await self.async_session.execute(stmt)
        result = response.scalars().all()
        return result

    async def get_by_id(self, id: UUID):
        stmt = select(self.model).where(self.model.id == id)
        response = await self.async_session.execute(stmt)
        result = response.scalar_one_or_none()
        return result

    async def get_filtered_by_params(self, **kwargs) -> list:
        res = await self.async_session.execute(select(self.model).filter_by(**kwargs))
        objects = res.scalars().all()
        return objects

    async def create(self, **kwargs):
        instance = self.model(**kwargs)
        self.async_session.add(instance)
        await self.async_session.commit()
        await self.async_session.refresh(instance)
        return instance

    async def update(self, id: UUID, **update_data):
        stmt = update(self.model).where(self.model.id == id).values(**update_data)
        await self.async_session.execute(stmt)
        await self.async_session.commit()
        return await self.get_by_id(id)

    async def delete(self, id: UUID) -> bool:
        async with self.async_session as s:
            stmt = delete(self.model).where(self.model.id == id)
            result = await s.execute(stmt)
            await s.commit()
            return result.rowcount > 0
