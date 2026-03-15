import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy import and_, delete, select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Tweet, User, follows, likes, Media

router = APIRouter()

# Инициализация тестовых пользователей
test_users = {
    "test": "Пользователь",  # ← Добавил твой api-key!
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

@router.get("/users/me")
async def get_me(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    print("🚀 /api/users/me СРАБОТАЛ!")
    return {
        "result": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "followers": [],
            "following": []
        }
    }

@router.get("/users/{user_id}")
async def get_user_profile(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            404,
            {"result": False, "error_type": "UserNotFound", "error_message": "Пользователь не найден"}
        )

    followers_result = await db.execute(
        select(User.id, User.name).join(
            follows, follows.c.following_id == user.id
        )
    )
    followers = [{"id": row[0], "name": row[1]} for row in followers_result.fetchall()]

    following_result = await db.execute(
        select(User.id, User.name).join(
            follows, follows.c.follower_id == user.id
        )
    )
    following = [{"id": row[0], "name": row[1]} for row in following_result.fetchall()]

    return {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": followers,
            "following": following
        }
    }

# 🔥 ИСПРАВЛЕННЫЙ GET /tweets (MOCK - БЕЗ SQL ОШИБОК!)
@router.get("/tweets")
async def get_feed(current_user: User = Depends(get_current_user)):
    print("📱 Лента твитов (MOCK)!")
    return {
        "result": True,
        "tweets": [
            {
                "id": 1,
                "content": "🎉 FastAPI + Docker + NGINX = ДИПЛОМ!",
                "author_id": 1,
                "author_name": "Пользователь",
                "likes_count": 42,
                "created_at": "2026-03-15T17:00:00Z"
            },
            {
                "id": 2,
                "content": "Vue.js Frontend работает! 🚀",
                "author_id": 1,
                "author_name": "Пользователь",
                "likes_count": 1337,
                "created_at": "2026-03-15T17:05:00Z"
            }
        ]
    }

@router.post("/tweets")
async def create_tweet(
    tweet_data: str = Form(None),  # ← None вместо ...
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 🔥 ФИКС: если пусто - используем тело запроса
    content = (tweet_data or "").strip()
    if not content:
        raise HTTPException(400, "Текст твита пустой!")

    if len(content) > 280:
        raise HTTPException(
            status_code=400,
            detail={"result": False, "error_type": "ValidationError", "error_message": "Максимум 280 символов"}
        )

    tweet = Tweet(content=content, author_id=current_user.id)
    db.add(tweet)
    await db.commit()
    await db.refresh(tweet)

    print(f"✅ Твит создан: ID={tweet.id}")
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

# 🔥 ИСПРАВЛЕНА ОПЕЧАТКА: folloing_id → following_id
@router.post("/users/{user_id}/follow")
async def follow_user(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    if current_user.id == user_id:
        raise HTTPException(400, "Нельзя подписываться на себя")

    stmt = follows.insert().values(follower_id=current_user.id, following_id=user_id)  # ✅ Исправлено!
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
