import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.database import engine, Base, get_db
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture(scope="session")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_db():
        return db_session
    app.dependency_overrides[get_db] = override_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
