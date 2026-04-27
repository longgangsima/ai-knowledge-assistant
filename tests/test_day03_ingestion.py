import asyncio

from app.db.chunk_repository import InMemoryChunkRepository, get_chunk_repository
from app.models.api import ChunkResponse, DocumentCreateRequest
from app.providers.embedding import MockEmbeddingProvider
from app.services.chunk import ChunkService
from app.services.embedding import EmbeddingService
from app.services.ingestion import IngestionService


def test_chunk_service_splits_paragraphs() -> None:
    chunks = ChunkService().split_text_into_chunks("First paragraph.\n\nSecond paragraph.")

    assert chunks == ["First paragraph.", "Second paragraph."]


def test_mock_embedding_provider_returns_stubbed_vector() -> None:
    vector = asyncio.run(
        EmbeddingService(MockEmbeddingProvider()).get_vector("some chunk text")
    )

    assert vector == [0.1, 0.2, 0.3]


def test_chunk_repository_lists_chunks_by_document_in_order() -> None:
    repository = InMemoryChunkRepository()

    asyncio.run(
        repository.save_many(
            [
                ChunkResponse(
                    chunk_id="chunk-2",
                    document_id="doc-1",
                    chunk_index=1,
                    text="Second chunk.",
                ),
                ChunkResponse(
                    chunk_id="chunk-1",
                    document_id="doc-1",
                    chunk_index=0,
                    text="First chunk.",
                ),
                ChunkResponse(
                    chunk_id="chunk-other",
                    document_id="doc-2",
                    chunk_index=0,
                    text="Other document.",
                ),
            ]
        )
    )

    chunks = asyncio.run(repository.list_by_document_id("doc-1"))

    assert [chunk.text for chunk in chunks] == ["First chunk.", "Second chunk."]


def test_ingestion_stores_chunks_with_stubbed_embeddings() -> None:
    response = asyncio.run(
        IngestionService().submit_document(
            DocumentCreateRequest(
                title="Day 3 Notes",
                content="First paragraph.\n\nSecond paragraph.",
                source="local-test",
            )
        )
    )

    chunks = asyncio.run(
        get_chunk_repository().list_by_document_id(response.document_id)
    )

    assert [chunk.chunk_index for chunk in chunks] == [0, 1]
    assert [chunk.text for chunk in chunks] == ["First paragraph.", "Second paragraph."]
    assert all(chunk.embedding == [0.1, 0.2, 0.3] for chunk in chunks)
    assert all(chunk.metadata == {"title": "Day 3 Notes", "source": "local-test"} for chunk in chunks)
