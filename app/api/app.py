import logging
import sys
from fastapi import FastAPI
from routes.scraper_router import router as scraper

# from data.database import shutdown_db_client, startup

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("uvicorn")

app = FastAPI(root_path="/api")
app.include_router(scraper, prefix="/scraper", tags=["scraper"])

# app.add_event_handler("startup", startup)
# app.add_event_handler("shutdown", shutdown_db_client)
