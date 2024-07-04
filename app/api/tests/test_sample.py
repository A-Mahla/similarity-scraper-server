import pytest


@pytest.mark.asyncio
async def test_add_sample_labeled(async_client):
    sample_data = {
        "prompt": "Example prompt",
        "output": "Example response",
        "label": True,
        "type": "unused",
    }
    # Now using the async_client directly
    response = await async_client.post("/sample/", json=sample_data)
    assert response.status_code == 201
    data = response.json()
    assert data["prompt"] == sample_data["prompt"]
    assert data["output"] == sample_data["output"]
    assert data["label"] == sample_data["label"]
    assert data["type"] == sample_data["type"]


@pytest.mark.asyncio
async def test_get_samples(async_client):
    response = await async_client.get("/sample/?type=training")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["samples"], list)


@pytest.mark.asyncio
async def test_delete_training_samples(async_client):
    response = await async_client.delete("/sample/?type=training")
    assert response.status_code == 200
    data = response.json()
    assert "deleted successfully" in data["message"]
