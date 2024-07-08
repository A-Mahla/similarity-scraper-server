import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_get_embeddings(async_client: AsyncClient):
    sample_data1 = {
        "metadata": {
            "url": "https://example1.com",
            "tag": "<p>",
            "language": "en",
            "type": "text",
            "content": "Example text content",
        }
    }
    sample_data2 = {
        "metadata": {
            "url": "https://example2.com",
            "tag": "<p>",
            "language": "en",
            "type": "text",
            "content": "Example text description",
        }
    }
    sample_data3 = {
        "metadata": {
            "url": "https://example3.com",
            "tag": "<p>",
            "language": "en",
            "type": "text",
            "content": "This test assumes that you can directly manipulate the test database by adding necessary entries before the test runs. This is crucial because the service logic depends on actual data.",
        }
    }

    await async_client.post("/sample", json=sample_data1)
    await async_client.post("/sample", json=sample_data2)
    await async_client.post("/sample", json=sample_data3)
    response = await async_client.get("/embedding/unique?type=text")
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    assert "samples_deleted" in response_data
    assert response_data["status"] == "success"
    assert response_data["message"] == "Similar embeddings are deleted successfully"
    assert len(response_data["samples_deleted"]) == 1

    for sample in response_data["samples_deleted"]:
        assert "vectors" in sample
        assert "sample" in sample
