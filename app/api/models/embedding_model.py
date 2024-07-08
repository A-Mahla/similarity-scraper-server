from pydantic import BaseModel, Field
from models.sample_model import Sample
from typing import Literal, List
from enum import Enum


class EmbeddingSampleType(str, Enum):
    TEXT = "text"
    IMAGE = "image"


class EmbeddingSample(BaseModel):
    sample: Sample = Field(..., title="Sample metadata")
    vectors: List[float] = Field(..., title="List of vectors")


class EmbeddingResponse(BaseModel):
    samples_deleted: List[EmbeddingSample] = Field(
        ..., title="Embedding sample metadata"
    )
    status: Literal["success", "failed"] = Field(
        "success", title="Status of the request"
    )
    message: str = Field(
        "Vectors were successfully extracted.",
        title="status message",
    )
