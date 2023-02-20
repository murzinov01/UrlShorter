import uvicorn
from fastapi import FastAPI

from .db.config import Base, engine
from .routers import urls
from .enums import Tags


description = """
UrlShorter API helps you generate short urls ans use them 🚀

## Urls

You will be able to:
* **create short url** - Generate short url based on full url
* **read full url** - Get full url by short link previously generated
* **delete urls** - Delete short url

## Additional
These endpoints are just for testing
You will be able to:

* **Read all urls** - Get all urls (short and full) stored in the system
* **Redirect** - Redirect to long url based on short one.
"""

tags_metadata = [
    {
        "name": Tags.urls.value,
        "description": "The main endpoints required in the test task",
    },
    {
        "name": Tags.additional.value,
        "description": "Additional endpoints which the author decided to add",
    },
]


app = FastAPI(
    title="UrlShorter",
    description=description,
    version="0.0.1",
    contact={
        "name": "Murzinov Michail",
        "email": "murzinov01@bk.ru",
    },
    openapi_tags=tags_metadata
)


@app.on_event("startup")
async def startup():
    # create db tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


app.include_router(urls.additional_router)
app.include_router(urls.router)


if __name__ == "__main__":
    uvicorn.run("app:app", port=8000, host="127.0.0.1")
