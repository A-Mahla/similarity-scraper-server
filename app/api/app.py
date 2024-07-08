import logging
import sys
from fastapi import FastAPI
from routes.scraper_router import router as scraper
from routes.embedding_router import router as embedding
from routes.sample_router import router as sample
from data.database import startup, shutdown_db_client

# from data.database import shutdown_db_client, startup

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("uvicorn")

app = FastAPI(root_path="/api")
app.include_router(scraper, prefix="/scraper", tags=["scraper"])
app.include_router(embedding, prefix="/embedding", tags=["embedding"])
app.include_router(sample, prefix="/sample", tags=["sample"])

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown_db_client)
