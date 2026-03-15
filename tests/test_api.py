import pytest
from httpx import AsyncClient


class TestTweets:
    @pytest.mark.asyncio
    async def test_create_tweet(self, client: AsyncClient):
        response = await client.post(
            "/api/tweets",
            headers={"api-key": "user1-1234-5678-9abc-def012345678"},
            data={"tweet_data": "Тест #1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True
        assert data["tweet_id"] > 0

    @pytest.mark.asyncio
    async def test_delete_own_tweet(self, client: AsyncClient):
        # Создаём твит
        resp = await client.post(
            "/api/tweets",
            headers={"api-key": "user1-1234-5678-9abc-def012345678"},
            data={"tweet_data": "Удаляемый"},
        )
        tweet_id = resp.json()["tweet_id"]

        # Удаляем
        response = await client.delete(f"/api/tweets/{tweet_id}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_like_unlike(self, client: AsyncClient):
        # Твит
        resp = await client.post(
            "/api/tweets",
            headers={"api-key": "user1-1234-5678-9abc-def012345678"},
            data={"tweet_data": "Лайкни меня"},
        )
        tweet_id = resp.json()["tweet_id"]

        # Like
        like_resp = await client.post(f"/api/tweets/{tweet_id}/likes")
        assert like_resp.status_code == 200

        # Unlike
        unlike_resp = await client.delete(f"/api/tweets/{tweet_id}/likes")
        assert unlike_resp.status_code == 200


class TestUsers:
    @pytest.mark.asyncio
    async def test_get_me(self, client: AsyncClient):
        response = await client.get(
            "/api/users/me", headers={"api-key": "user1-1234-5678-9abc-def012345678"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["name"] == "Иван Иванов"

    @pytest.mark.asyncio
    async def test_follow_user(self, client: AsyncClient):
        # Подписываемся на user2
        response = await client.post(
            "/api/users/2/follow",
            headers={"api-key": "user1-1234-5678-9abc-def012345678"},
        )
        assert response.status_code == 200
