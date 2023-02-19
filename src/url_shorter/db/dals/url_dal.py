from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.url import Url


class UrlDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_all_urls(self, skip: int = 0, limit: int = 100):
        result = await self.db_session.execute(select(Url).order_by(Url.id).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_url(self, short_url: str):
        result = await self.db_session.execute(select(Url).where(Url.short_url == short_url))
        return result.scalars().first()

    async def get_short_utl(self, url: str):
        result = await self.db_session.execute(select(Url).where(Url.url == url))
        return result.scalars().first()

    async def create_url(self, url: str, short_url: str):
        new_url = Url(url=url, short_url=short_url)
        self.db_session.add(new_url)
        await self.db_session.flush()

    async def delete_url(self, short_url: str):
        await self.db_session.execute(delete(Url).where(Url.short_url == short_url))
