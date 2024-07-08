from fastapi import HTTPException
from models.sample_model import (
    Sample,
    SampleResponse,
    SamplesResponse,
    DeleteSamplesResponse,
    ExtendedSampleType,
    GroupSampleType,
    SampleType,
    DeleteUniqueSampleResponse,
)
import logging
from beanie import PydanticObjectId

logger = logging.getLogger("uvicorn")


class SampleService:

    @staticmethod
    async def add_sample(sample: Sample) -> SampleResponse:
        try:
            existing_sample = await Sample.find_one(
                Sample.metadata.url == sample.metadata.url,
            )
            if existing_sample:
                return SampleResponse(
                    id=str(existing_sample.id),
                    metadata=existing_sample.metadata,
                    message="Sample already exists and was not added.",
                )

            await sample.insert()
            return SampleResponse(id=str(sample.id), metadata=sample.metadata)
        except Exception:
            logger.error("Failed to add sample", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail="Failed to add sample",
            )

    @staticmethod
    async def delete_sample_by_type(type: ExtendedSampleType) -> DeleteSamplesResponse:
        try:
            if isinstance(type, GroupSampleType):
                if type.value == "all":
                    result = await Sample.find().delete_many()
                    count = result.deleted_count if result is not None else 0
                    message = f"all samples ({count}) are deleted successfully"
                else:
                    raise ValueError(
                        f"Unsupported group type: {type}. Have to be implemented."
                    )
            else:
                result = await Sample.find(Sample.metadata.type == type).delete_many()
                count = result.deleted_count if result is not None else 0
                message = f"{count} samples of type '{type.value}' deleted successfully"
            return DeleteSamplesResponse(count=count, message=message)
        except Exception:
            logger.error("Failed to delete training samples: ", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to delete '{type.value}' samples",
            )

    @staticmethod
    async def delete_sample_by_id(id: PydanticObjectId) -> DeleteUniqueSampleResponse:
        try:
            result = await Sample.find(Sample.id == id).delete()
            if result is None:
                raise ValueError(f"Sample with id '{id}' not found")
            message = f"Sample with id '{id}' deleted successfully"
            return DeleteUniqueSampleResponse(message=message)
        except Exception:
            logger.error("Failed to delete training samples: ", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to delete sample with id '{id}'",
            )

    @staticmethod
    async def get_samples(type: ExtendedSampleType) -> SamplesResponse:
        try:
            if isinstance(type, GroupSampleType):
                if type.value == "all":
                    logger.info("Getting all samples")
                    samples = await Sample.find().to_list(None)
                else:
                    raise ValueError(
                        f"Unsupported group type: {type.value}. Have to be implemented."
                    )
            else:
                samples = await Sample.find(Sample.metadata.type == type).to_list(None)

            return SamplesResponse(
                samples=[Sample(**sample.model_dump()) for sample in samples]
            )
        except Exception:
            logger.error("Failed to get samples: ", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get '{type.value}' samples",
            )
