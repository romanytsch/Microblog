import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.database import get_db
from app.main import app

# База для тестов
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@db:5432/test_db"


@pytest.fixture(scope="session")
async def test_db_engine():
    """Создаёт движок БД для тестов"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        from app.models import Base
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(test_db_engine):  # ✅ ИСПРАВЛЕНО!
    """AsyncSession для каждого теста"""
    async_session = async_sessionmaker(test_db_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession):
    """AsyncClient для API тестов"""

    async def override_db_dependency():
        return db_session

    app.dependency_overrides[get_db] = override_db_dependency

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
