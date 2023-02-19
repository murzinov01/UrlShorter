import uvicorn
from fastapi import FastAPI

from .db.config import Base, engine
from .routers import urls

app = FastAPI()


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
