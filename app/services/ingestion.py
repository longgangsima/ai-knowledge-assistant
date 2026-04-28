from uuid import uuid4

from app.db import (get_chunk_repository, get_document_repository,
                    get_job_repository)
from app.models.api import (ChunkResponse, DocumentCreateRequest,
                            DocumentCreateResponse, JobResponse)
from app.providers.embedding import MockEmbeddingProvider
from app.services.chunk import ChunkService
from app.services.embedding import EmbeddingService


class IngestionService:
    async def submit_document(self, payload: DocumentCreateRequest) -> DocumentCreateResponse:
        document_id = str(uuid4())
        job_id = str(uuid4())

        job = JobResponse(
            job_id=job_id,
            document_id=document_id,
            status="queued",
            detail=f"Queued ingestion for document '{payload.title}'.",
        )

        await get_job_repository().save(job)

        chunks = ChunkService().split_text_into_chunks(payload.content)
        embedding_provider = MockEmbeddingProvider()
        embedding_service = EmbeddingService(embedding_provider)

        for chunk_index, chunk_text in enumerate(chunks):
            vectors = await embedding_service.get_vector(chunk_text)
            chunk = ChunkResponse(
                chunk_id=str(uuid4()),
                document_id=document_id,
                chunk_index=chunk_index,
                text=chunk_text,
                embedding=vectors,
                metadata={
                    "title": payload.title,
                    "source": payload.source or "",
                },
            )

            await get_chunk_repository().save(chunk)

        document = DocumentCreateResponse(
            document_id=document_id,
            job_id=job_id,
            status="queued",
        )

        await get_document_repository().save(document)

        return document

    # async def ge