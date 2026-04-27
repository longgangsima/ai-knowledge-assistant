from app.models.api import ChunkResponse


class InMemoryChunkRepository:
    def __init__(self) -> None:
        self._chunks: dict[str, ChunkResponse] = {}

    async def save(self, chunk: ChunkResponse) -> None:
        self._chunks[chunk.chunk_id] = chunk

    async def save_many(self, chunks: list[ChunkResponse]) -> None:
        for chunk in chunks:
            await self.save(chunk)

    async def get(self, chunk_id: str) -> ChunkResponse | None:
        return self._chunks.get(chunk_id)

    async def list_by_document_id(self, document_id: str) -> list[ChunkResponse]:
        chunks = [
            chunk
            for chunk in self._chunks.values()
            if chunk.document_id == document_id
        ]
        return sorted(chunks, key=lambda chunk: chunk.chunk_index)

_chunk_repository = InMemoryChunkRepository()


def get_chunk_repository() -> InMemoryChunkRepository:
    return _chunk_repository
