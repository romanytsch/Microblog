import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from app.main import app
from app.database import get_db
from app.api.endpoints import get_current_user


class MockUser:
    """Мок пользователя для тестов"""

    def __init__(self):
        self.id = 1
        self.name = "Тестовый пользователь"
        self.api_key = "test"


class MockSession:
    """Полный мок сессии БД"""

    async def execute(self, query):
        result = MockResult()
        return result

    async def commit(self): pass

    async def refresh(self, *args): pass


class MockResult:
    """Мок результата запроса"""

    def first(self):
        return MockUser()

    async def scalar_one_or_none(self):
        return None  # Для get_current_user


@pytest_asyncio.fixture
async def client():
    """Тестовый клиент с полным мок"""

    async def mock_get_db():
        yield MockSession()

    async def mock_get_current_user(api_key: str):
        return MockUser()  # 🔥 Возвращаем User объект!

    # Мокаем ОБА dependency
    app.dependency_overrides[get_db] = mock_get_db
    app.dependency_overrides[get_current_user] = mock_get_current_user

    async with AsyncClient(app=app, base_url="http://test", transport=ASGITransport(app=app)) as ac:
        yield ac

    app.dependency_overrides.clear()
