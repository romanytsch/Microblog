from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.endpoints import router
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы базы данных созданы!")
    yield
    print("Завершение работы приложения")


app = FastAPI(fitle="Microblog API", docs_url="/docs", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router, prefix="/api", tags=["api"])


@app.get("/")
async def root():
    return {"message": "Microblog API готов!"}
