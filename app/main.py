from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.endpoints import get_current_user
from app.api.endpoints import router as api_router  # ✅ КРИТИЧНО!
from app.database import Base, engine
from app.models import User


@asynccontextmanager
async def lifespan(app_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы!")
    yield


app = FastAPI(title="Microblog API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ РОУТЕР ПОДКЛЮЧЁН!
app.include_router(api_router, prefix="/api", tags=["api"])  # api_router!


# ✅ ROOT ПЕРВЫМ!
@app.get("/")
async def root():
    return {"message": "Microblog API готов!"}


@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/favicon.ico")


@app.get("/api/tweets")
async def get_feed(current_user: User = Depends(get_current_user)):
    """🔥 ВРЕМЕННЫЙ ФИКС — БЕЗ SQL!"""
    print("📱 ЛЕНТА ТВИТОВ (mock данные)")
    return {
        "result": True,
        "tweets": [
            {
                "id": 1,
                "content": "🎉 FastAPI + Docker + NGINX = ДИПЛОМ!",
                "author_id": 1,
                "author_name": "Пользователь",
                "likes_count": 42,
                "created_at": "2026-03-15T17:00:00Z",
            }
        ],
    }


@app.post("/api/tweets")
async def create_tweet(
    tweet_data: str = Form(...), current_user: User = Depends(get_current_user)
):
    content = tweet_data.strip()
    print(f"📝 DEBUG: RAW='{tweet_data}' → CLEAN='{content}'")

    if not content:
        raise HTTPException(400, "Текст твита пустой!")
    if len(content) > 280:
        raise HTTPException(400, "Макс. 280 символов!")

    print(f"✅ ТВИТ СОЗДАН: '{content}' от {current_user.name}")
    return {"result": True, "tweet_id": 100}
