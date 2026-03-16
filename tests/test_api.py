import pytest

class TestAPI:
    @pytest.mark.asyncio
    async def test_get_users_me(self, client):
        response = await client.get("/api/users/me", headers={"api-key": "test"})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_tweet(self, client):
        response = await client.post(
            "/api/tweets",
            json={"content": "Тест pytest"},
            headers={"api-key": "test"}
        )

        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_get_tweets(self, client):
        response = await client.get("/api/tweets", headers={"api-key": "test"})

        assert response.status_code == 422
