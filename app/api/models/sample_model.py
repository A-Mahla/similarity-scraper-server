from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from typing import Union
from enum import Enum


class SampleType(str, Enum):
    USED = "used"
    TRAINING = "training"


class GroupSampleType(str, Enum):
    ALL = "all"


ExtendedSampleType = Union[SampleType, GroupSampleType]


class ChatSampleRequest(BaseModel):
    prompt: str = Field(..., description="The prompt given to the model")
    output: str = Field(..., description="The output from the model")
    label: bool = Field(..., description="The label of the sample")
    type: SampleType = Field(
        SampleType.TRAINING,
        description="Whether the sample has been used for training actual model or not",
    )


class ChatSample(Document):
    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
    )
    prompt: str = Field(..., description="The prompt given to the model")
    output: str = Field(..., description="The output from the model")
    label: bool = Field(..., description="The label of the sample")
    type: SampleType = Field(
        SampleType.TRAINING,
        description="Whether the sample has been used for training actual model or not",
    )

    class Settings:
        collection = "chat_samples"

    class ConfigDict:
        json_encoders = {
            PydanticObjectId: str  # Ensures ObjectId is converted to string when serializing to JSON
        }


class ChatSampleResponse(BaseModel):
    id: str = Field(..., description="The unique identifier for the chat sample")
    prompt: str = Field(..., description="The prompt given to the model")
    output: str = Field(..., description="The output from the model")
    label: bool = Field(..., description="The label of the sample")
    type: SampleType = Field(..., description="Usage status of the sample")
    message: str = Field(
        default="Sample created successfully",
        description="A message about the result of the operation",
    )


class SamplesResponse(BaseModel):
    samples: list[ChatSample] = Field(..., description="A list of chat samples")
    message: str = Field(
        default="Samples retrieved successfully",
        description="A message about the result of the operation",
    )


class DeleteSamplesResponse(BaseModel):
    message: str = Field(
        default="Samples deleted successfully",
        description="A message about the result of the operation",
    )
