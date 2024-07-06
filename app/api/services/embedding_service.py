from fastapi import HTTPException
from models.embedding_model import EmbeddingResponse, EmbeddingSample
from models.sample_model import SampleType, SamplesResponse, Sample
from services.sample_service import SampleService
import torch
from typing import Tuple, List
import httpx
import logging
import json
import os


logger = logging.getLogger("uvicorn")


class EmbeddingService:

    @staticmethod
    async def get_embeddings(
        type: SampleType,
    ) -> Tuple[list[list[float]], SamplesResponse]:

        try:
            data = await SampleService.get_samples(type)
            text_content, image_content = [], []
            if type == SampleType.TEXT:
                clip_key = "textVectors"
                text_content = [sample.metadata.content for sample in data.samples]
            else:
                clip_key = "imageVectors"
                image_content = [sample.metadata.content for sample in data.samples]
            url = f'{os.environ["CLIP_INFERENCE_API"]}/vectorize'
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            content = json.dumps({"texts": text_content, "images": image_content})

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, content=content)
                if response.status_code == 200:
                    response_data = response.json()
                    vectors = response_data.get(clip_key, [])
                else:
                    raise ValueError("Failed to get embeddings")

        except Exception:
            HTTPException(status_code=400, detail="Failed to get embeddings")

        return vectors, data

    @staticmethod
    def compute_similarity(
        vectors: list[list[float]], samples: list[Sample]
    ) -> List[Tuple[Sample, Sample, list[float]]]:

        embeddings = torch.tensor(vectors, dtype=torch.float32)
        similarity_matrix = torch.mm(embeddings, embeddings.T)
        threshold = 0.85

        similarity = []
        for i in range(embeddings.size(0)):
            for j in range(i + 1, embeddings.size(0)):
                if similarity_matrix[i, j] > threshold:
                    similarity.append((samples[i], samples[j], vectors[j]))

        return similarity

    @staticmethod
    async def delete_duplicate_samples(
        similarity: List[Tuple[Sample, Sample, list[float]]]
    ) -> set[Tuple[Sample, list[float]]]:
        deleted = set()
        for i, j, vector_j in similarity:
            if i.id not in deleted and j.id not in deleted:
                try:
                    await SampleService.delete_sample_by_id(j.id)
                    deleted.add((j, vector_j))
                except Exception:
                    logger.error(
                        f"Failed to delete duplicate samples with id : {j.id}",
                        exc_info=True,
                    )

        return deleted

    @staticmethod
    async def delete_duplicate_embedding_samples(
        type: SampleType,
    ) -> EmbeddingResponse:

        vectors, data = await EmbeddingService.get_embeddings(type)
        if len(vectors) != len(data.samples):
            raise HTTPException(
                status_code=400,
                detail="Number of vectors and samples do not match.",
            )
        similar_embedding_samples = EmbeddingService.compute_similarity(
            vectors, data.samples
        )
        embedding_deleted = await EmbeddingService.delete_duplicate_samples(
            similar_embedding_samples
        )

        return EmbeddingResponse(
            embedding_samples=[
                EmbeddingSample(vectors=v, sample=s) for s, v in embedding_deleted
            ],
            status="success",
            message="Similar embeddings are deleted successfully",
        )
