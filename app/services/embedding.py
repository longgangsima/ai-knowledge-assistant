from app.providers.embedding import EmbeddingProvider


class EmbeddingService:
    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    async def get_vector(self, text: str) -> list[float]:
        return await self.provider.embed_text(text)
