import tempfile

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_media(client: AsyncClient):
    # Создаём тестовое изображение
    with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
        tmp.write(b"fake image data")
        tmp.flush()

        with open(tmp.name, "rb") as f:
            response = await client.post(
                "/api/medias",
                headers={"api-key": "user1-1234-5678-9abc-def012345678"},
                files={"file": ("test.jpg", f, "image/jpeg")},
            )

    assert response.status_code == 200
    assert response.json()["result"] is True
