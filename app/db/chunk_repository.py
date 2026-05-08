from app.models.api import ChunkResponse


class InMemoryChunkRepository:
    def __init__(self) -> None:
        """Create the in-memory chunk store used by the local retrieval path."""
        self._chunks: dict[str, ChunkResponse] = {}

    async def save(self, chunk: ChunkResponse) -> None:
        """Persist one chunk record by chunk id."""
        self._chunks[chunk.chunk_id] = chunk

    async def save_many(self, chunks: list[ChunkResponse]) -> None:
        """Persist multiple chunk records through the same single-save path."""
        for chunk in chunks:
            await self.save(chunk)

    async def get(self, chunk_id: str) -> ChunkResponse | None:
        """Return one chunk by id when it exists."""
        return self._chunks.get(chunk_id)

    async def list_by_document_id(self, document_id: str) -> list[ChunkResponse]:
        """Return chunks for one document in original chunk order."""
        chunks = [
            chunk
            for chunk in self._chunks.values()
            if chunk.document_id == document_id
        ]
        return sorted(chunks, key=lambda chunk: chunk.chunk_index)

    async def list_all(self) -> list[ChunkResponse]:
        """Return all stored chunks in stable order for retrieval."""
        return sorted(
            self._chunks.values(),
            key=lambda chunk: (chunk.document_id, chunk.chunk_index),
        )

_chunk_repository = InMemoryChunkRepository()


def get_chunk_repository() -> InMemoryChunkRepository:
    return _chunk_repository
