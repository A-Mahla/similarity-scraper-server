from beanie import Document, PydanticObjectId
from models.scraper_model import ScraperMetaData, ScraperType
from pydantic import BaseModel, Field
from typing import Union
from enum import Enum


SampleType = ScraperType


class GroupSampleType(str, Enum):
    ALL = "all"


ExtendedSampleType = Union[SampleType, GroupSampleType]


class SampleRequest(BaseModel):
    metadata: ScraperMetaData = Field(..., description="The metadata of the sample")


class Sample(Document):
    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
    )
    metadata: ScraperMetaData = Field(..., description="The metadata of the sample")

    class Settings:
        collection = "http_samples"

    class ConfigDict:
        json_encoders = {PydanticObjectId: str}


class SampleResponse(BaseModel):
    id: str = Field(..., description="The unique identifier for the http sample")
    metadata: ScraperMetaData = Field(..., description="The metadata of the sample")
    message: str = Field(
        default="Sample created successfully",
        description="A message about the result of the operation",
    )


class SamplesResponse(BaseModel):
    samples: list[Sample] = Field(..., description="A list of http samples")
    message: str = Field(
        default="Samples retrieved successfully",
        description="A message about the result of the operation",
    )


class DeleteUniqueSampleResponse(BaseModel):
    message: str = Field(
        default="Samples deleted successfully",
        description="A message about the result of the operation",
    )


class DeleteSamplesResponse(BaseModel):
    count: int = Field(..., description="The number of samples deleted")
    message: str = Field(
        default="Samples deleted successfully",
        description="A message about the result of the operation",
    )
