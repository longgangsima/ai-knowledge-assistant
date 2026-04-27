class EmbeddingProvider:
    async def embed_text(self, text: str) -> list[float]:
        raise NotImplementedError("Embedding providers must implement embed_text.")


class MockEmbeddingProvider(EmbeddingProvider):
    async def embed_text(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]
