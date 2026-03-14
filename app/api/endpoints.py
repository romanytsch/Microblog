import os
import uuid

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy import and_, delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Tweet, User, follows, likes

router = APIRouter()

# Инициализация тестовых пользователей
test_users = {
    "user1": "Иван Иванов",
    "user2": "Мария Петрова",
}


async def get_current_user(
    api_key: str = Header(None), db: AsyncSession = Depends(get_db)
) -> User:
    if not api_key:
        raise HTTPException(401, "Отсутствует ключ API")

    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalar_one_or_none()

    if not user:
        # Создание пользователя при первом обращении
        user = User(api_key=api_key, name=test_users.get(api_key, "Пользователь"))
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


@router.post("/tweets")
async def create_tweet(
    tweet_data: str = Form(..., min_length=1, max_length=280),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not 1 <= len(tweet_data.strip()) <= 280:
        raise HTTPException(400, "Текст твита не 1 - 280 символов")

    tweet = Tweet(content=tweet_data, author_id=current_user.id)
    db.add(tweet)
    await db.commit()
    await db.refresh(tweet)
    return {"result": True, "tweet_id": tweet.id}


@router.delete("/tweets/{tweet_id}")
async def delete_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        delete(Tweet).where(
            and_(Tweet.id == tweet_id, Tweet.author_id == current_user.id)
        )
    )
    if result.rowcount == 0:
        raise HTTPException(404, "Твит не найден или не ваш")
    await db.commit()
    return {"result": True}


@router.post("/tweets/{tweet_id}/likes")
async def like_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = likes.insert().values(user_id=current_user.id, tweet_id=tweet_id)
    try:
        await db.execute(stmt)
        await db.commit()
    except:
        raise HTTPException(400, "Лайк уже поставлен")
    return {"result": True}


@router.delete("/tweets/{tweet_id}/likes")
async def unlike_tweet(
    tweet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        delete(likes).where(
            and_(likes.c.user_id == current_user.id, likes.c.tweet_id == tweet_id)
        )
    )
    await db.commit()
    return {"result": True}


@router.post("/users/{user_id}/follow")
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.id == user_id:
        raise HTTPException(400, "Нельзя подписываться на себя")

    stmt = follows.insert().values(follower_id=current_user.id, folloing_id=user_id)
    try:
        await db.execute(stmt)
        await db.commit()
    except:
        raise HTTPException(400, "Уже подписаны")
    return {"result": True}


@router.delete("/users/{user_id}/follow")
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        delete(follows).where(
            and_(
                follows.c.follower_id == current_user.id,
                follows.c.following_id == user_id,
            )
        )
    )
    await db.commit()
    return {"result": True}


@router.post("/medias")
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Только изображения")

    filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    filepath = os.path.join("static/media", filename)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"result": True, "media_id": 1}


@router.get("/tweets")
async def get_feed(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(follows.c.following_id).where(follows.c.follower_id == current_user.id)
    )
    following_ids = result.scalars().all()

    result = await db.execute(
        select(Tweet)
        .filter(Tweet.author_id.in_(following_ids))
        .order_by(func.count(likes.c.tweet_id).desc(), Tweet.created_at.desc())
    )
    tweets = result.scalars().all()

    return {"result": True, "tweets": []}


@router.get("/users/me")
async def get_me(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return {
        "result": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "followers": [],
            "following": [],
        },
    }
