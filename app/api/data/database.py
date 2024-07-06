import logging
import os
from beanie import init_beanie
from models.sample_model import Sample
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

logger = logging.getLogger("uvicorn")


async def instantiate_database():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    await init_beanie(
        database=client[os.environ["MONGO_INITDB_DATABASE"]],
        document_models=[
            Sample,
        ],
    )


async def check_db_connection() -> bool:
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    try:
        await client.admin.command("ping")
        logger.info("Connected to the MongoDB database!")
        return True
    except Exception as e:
        logger.info(f"Error connecting to the MongoDB database: {e}")
        return False
    finally:
        client.close()


async def startup():
    await instantiate_database()
    await check_db_connection()


async def shutdown_db_client():
    client = MongoClient(os.environ["MONGO_URL"])
    client.close()
    print("Disconnected from the MongoDB database!")


async def shutdown():
    await shutdown_db_client()
