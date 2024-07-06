from fastapi import APIRouter, status, Body, Query
from models.sample_model import (
    Sample,
    SampleRequest,
    SampleResponse,
    SamplesResponse,
    DeleteSamplesResponse,
    ExtendedSampleType,
)
from services.sample_service import SampleService
import logging


router = APIRouter()
logger = logging.getLogger("uvicorn")


# curl -X POST http://localhost/api/sample \
# -H "Content-Type: application/json" \
# -d '{
#     "metadata": {
#         "url": "https://www.exampletextpage.com",
#         "tag": "<p>",
#         "language": "en",
#         "type": "text",
#         "content": "This is a sample text content for the labeled dataset."
#     }
# }'
@router.post(
    "/",
    response_description="Add a new sample",
    status_code=status.HTTP_201_CREATED,
    response_model=SampleResponse,
)
async def add_sample_labeled(
    sample: SampleRequest = Body(...),
) -> SampleResponse:
    logger.info(f"Adding sample: {sample}")
    return await SampleService.add_sample(Sample(**sample.model_dump()))


# curl -X DELETE "http://localhost/api/sample/?type=text" -H "accept: application/json"
@router.delete(
    "/",
    response_description="Delete samples",
    status_code=status.HTTP_200_OK,
    response_model=DeleteSamplesResponse,
)
async def delete_training_samples(
    type: ExtendedSampleType = Query(...),
) -> DeleteSamplesResponse:
    return await SampleService.delete_sample_by_type(type)


# curl -X GET "http://localhost/api/?type=text" -H "accept: application/json"
@router.get(
    "/",
    response_description="Get samples",
    status_code=status.HTTP_200_OK,
    response_model=SamplesResponse,
)
async def get_samples(type: ExtendedSampleType = Query(...)) -> SamplesResponse:
    return await SampleService.get_samples(type)
