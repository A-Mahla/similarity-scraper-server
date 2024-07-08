import pytest


@pytest.mark.asyncio
async def test_add_sample(async_client):
    response = await async_client.post(
        "/sample/",
        json={
            "metadata": {
                "url": "https://www.exampletextpage.com",
                "tag": "<p>",
                "language": "en",
                "type": "text",
                "content": "This is a sample text content for the labeled dataset.",
            }
        },
    )
    assert response.status_code == 201
    assert response.json()["message"] == "Sample created successfully"


@pytest.mark.asyncio
async def test_get_samples(async_client):
    response = await async_client.get("sample/?type=text")
    assert response.status_code == 200
    assert response.json()["message"] == "Samples retrieved successfully"
    assert isinstance(response.json()["samples"], list)


@pytest.mark.asyncio
async def test_delete_samples(async_client):
    response = await async_client.delete("sample/?type=text")
    assert response.status_code == 200
    assert response.json()["message"] == "1 samples of type 'text' deleted successfully"
    assert "count" in response.json()
