from fastapi import APIRouter, status, Query
from models.embedding_model import EmbeddingResponse
from models.sample_model import SampleType
from services.embedding_service import EmbeddingService
import logging


router = APIRouter()
logger = logging.getLogger("uvicorn")


# curl -X GET "http://localhost/api/embedding/unique?type=text" -H "accept: application/json"
@router.get(
    "/unique",
    response_description="Get all embeddings",
    status_code=status.HTTP_200_OK,
    response_model=EmbeddingResponse,
)
async def get_embeddings(type: SampleType = Query(...)) -> EmbeddingResponse:
    return await EmbeddingService.delete_duplicate_embedding_samples(type)
