import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_scrape_page(async_client: AsyncClient):
    # Test data setup
    request_payload = {"url": "https://www.hcompany.ai/", "image_search": False}

    expected_response = {
        "metadata": {
            "url": "https://www.hcompany.ai/",
            "image_url": None,
            "tag": "section",
            "language": "en",
            "type": "text",
            "content": "H  is  working on frontier action models,  to boost the productivity of workers Outrageous AI capabilities for task automation & decision-making. Join us",
        },
        "status": "success",
        "message": "Text content was successfully extracted from the page.",
        "database_log": "Sample created successfully",
    }

    response = await async_client.post("/scraper", json=request_payload)
    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()
    assert (
        response_data == expected_response
    ), "Response data does not match the expected output."

    assert (
        response_data["metadata"]["url"] == request_payload["url"]
    ), "URL in the response does not match the request."
    assert response_data["metadata"]["content"], "The content should not be empty."
