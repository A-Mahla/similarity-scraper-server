from fastapi import HTTPException
from models.sample_model import (
    ChatSample,
    ChatSampleResponse,
    SamplesResponse,
    DeleteSamplesResponse,
    ExtendedSampleType,
    GroupSampleType,
    SampleType,
)
import logging


logger = logging.getLogger("uvicorn")


class SampleService:

    @staticmethod
    async def add_sample(sample: ChatSample) -> ChatSampleResponse:
        try:
            existing_sample = await ChatSample.find_one(
                ChatSample.prompt == sample.prompt, ChatSample.output == sample.output
            )
            if existing_sample:
                return ChatSampleResponse(
                    id=str(existing_sample.id),
                    prompt=existing_sample.prompt,
                    output=existing_sample.output,
                    label=existing_sample.label,
                    type=existing_sample.type,
                    message="Sample already exists and was not added.",
                )

            await sample.insert()
            return ChatSampleResponse(
                id=str(sample.id),
                prompt=sample.prompt,
                output=sample.output,
                label=sample.label,
                type=sample.type,
            )
        except Exception:
            logger.error("Failed to add sample", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail="Failed to add sample",
            )

    @staticmethod
    async def delete_training_sample(type: ExtendedSampleType) -> DeleteSamplesResponse:
        try:
            if type is not SampleType.TRAINING:
                raise ValueError(
                    f"The type '{type.value}' is intentionally disabled to prevent accidental deletion. "
                    "Please comment out this line to proceed."
                )

            if isinstance(type, GroupSampleType):
                if type.value == "all":
                    result = await ChatSample.find().delete_many()
                    count = result.deleted_count if result is not None else 0
                    message = f"all samples ({count}) are deleted successfully"
                else:
                    raise ValueError(
                        f"Unsupported group type: {type}. Have to be implemented."
                    )
            else:
                result = await ChatSample.find(ChatSample.type == type).delete_many()
                count = result.deleted_count if result is not None else 0
                message = f"{count} samples of type '{type}' deleted successfully"
            return DeleteSamplesResponse(message=message)
        except Exception:
            logger.error("Failed to delete training samples: ", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to delete '{type.value}' samples",
            )

    @staticmethod
    async def get_samples(type: ExtendedSampleType) -> SamplesResponse:
        try:
            if isinstance(type, GroupSampleType):
                if type.value == "all":
                    logger.info("Getting all samples")
                    samples = await ChatSample.find().to_list(None)
                else:
                    raise ValueError(
                        f"Unsupported group type: {type}. Have to be implemented."
                    )
            else:
                samples = await ChatSample.find(ChatSample.type == type).to_list(None)

            return SamplesResponse(
                samples=[ChatSample(**sample.model_dump()) for sample in samples]
            )
        except Exception:
            logger.error("Failed to get samples: ", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to get '{type.value}' samples",
            )
