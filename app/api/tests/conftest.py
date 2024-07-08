import pytest_asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from httpx import AsyncClient
from app import app  # type: ignore
import asyncio
from models.sample_model import Sample
from httpx._transports.asgi import ASGITransport


@pytest_asyncio.fixture(scope="session", autouse=True)
async def async_client():
    client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
    client.get_io_loop = asyncio.get_running_loop
    await client.admin.command("ping")
    await init_beanie(database=client["test_db"], document_models=[Sample])

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test/api"
    ) as ac:
        try:
            yield ac
        finally:
            await client.drop_database("test_db")
            client.close()
