from fastapi import APIRouter, status, Body, Query
from models.sample_model import (
    ChatSample,
    ChatSampleRequest,
    ChatSampleResponse,
    SamplesResponse,
    DeleteSamplesResponse,
    ExtendedSampleType,
)
from services.sample_service import SampleService
import logging


router = APIRouter()
logger = logging.getLogger("uvicorn")


# curl -X POST "http://yourdomain.com/sample/" \
#      -H "Content-Type: application/json" \
#      -d '{
#          "prompt": "Example prompt",
#          "output": "Example response",
#          "label": true,
#          "type": "training" # default is "unused"
#     }'
@router.post(
    "/",
    response_description="Add a new sample to the labeled dataset",
    status_code=status.HTTP_201_CREATED,
    response_model=ChatSampleResponse,
)
async def add_sample_labeled(
    sample: ChatSampleRequest = Body(...),
) -> ChatSampleResponse:
    logger.info(f"Adding sample: {sample}")
    return await SampleService.add_sample(ChatSample(**sample.model_dump()))


# curl -X DELETE "http://yourdomain.com/sample/?type=unused" -H "accept: application/json"
@router.delete(
    "/",
    response_description="Delete all training samples",
    status_code=status.HTTP_200_OK,
    response_model=DeleteSamplesResponse,
)
async def delete_training_samples(
    type: ExtendedSampleType = Query(...),
) -> DeleteSamplesResponse:
    return await SampleService.delete_training_sample(type)


# curl -X GET "http://yourdomain.com/sample/?type=unused" -H "accept: application/json"
@router.get(
    "/",
    response_description="Get all samples",
    status_code=status.HTTP_200_OK,
    response_model=SamplesResponse,
)
async def get_samples(type: ExtendedSampleType = Query(...)) -> SamplesResponse:
    return await SampleService.get_samples(type)
