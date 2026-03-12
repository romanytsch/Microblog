from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

DATABASE_URL = (f"postgresql+asyncpg://"
                f"{os.getenv('POSTGRES_USER')}:"
                f"{os.getenv('POSTGRES_PASSWORD')}@"
                f"{os.getenv('POSTGRES_HOST')}:"
                f"{os.getenv('POSTGRES_PORT')}/"
                f"{os.getenv('POSTGRES_DB')}")

engine = create_async_engine(DATABASE_URL, echo=True, pool_pre=True)
AsyncSessionLocal = async_sessionmaker(engine,
                                       class_=AsyncSession,
                                       expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
