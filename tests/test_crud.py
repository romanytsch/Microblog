import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, follows


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    user = User(api_key="crud-123", name="CRUD User")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    assert user.id > 0


@pytest.mark.asyncio
async def test_follow_unfollow(db_session: AsyncSession):
    user1 = User(api_key="u1", name="User1")
    user2 = User(api_key="u2", name="User2")
    db_session.add_all([user1, user2])
    await db_session.commit()

    # Follow
    stmt = follows.insert().values(follower_id=user1.id, following_id=user2.id)
    await db_session.execute(stmt)
    await db_session.commit()

    # Check follow
    result = await db_session.execute(
        select(follows.c.following_id).filter(follows.c.follower_id == user1.id)
    )
    assert result.scalar() == user2.id
