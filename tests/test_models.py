import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tweet, User


@pytest.mark.asyncio
async def test_user_model(db_session: AsyncSession):
    user = User(api_key="test-123", name="Тест")
    db_session.add(user)
    await db_session.commit()

    result = await db_session.execute(select(User).filter(User.api_key == "test-123"))
    db_user = result.scalar_one_or_none()
    assert db_user.name == "Тест"
    assert db_user.id == user.id


@pytest.mark.asyncio
async def test_tweet_model(db_session: AsyncSession):
    user = User(api_key="author-123", name="Автор")
    tweet = Tweet(content="Тест твит", author_id=user.id)

    db_session.add_all([user, tweet])
    await db_session.commit()

    result = await db_session.execute(select(Tweet).filter(Tweet.id == tweet.id))
    db_tweet = result.scalar_one_or_none()
    assert db_tweet.content == "Тест твит"
    assert db_tweet.author_id == user.id
