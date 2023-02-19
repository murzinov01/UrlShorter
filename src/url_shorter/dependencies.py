from .db.config import async_session
from .db.dals.url_dal import UrlDAL


async def get_url_dal():
    async with async_session() as session:
        async with session.begin():
            yield UrlDAL(session)
