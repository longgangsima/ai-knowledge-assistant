from collections.abc import AsyncIterator

from app.models.api import ChunkResponse


class ChatService:
    async def generate_answer(self, question: str, chunks: list[ChunkResponse]) -> str:
        """Generate an answer from retrieved chunks behind a replaceable service boundary."""
        if not chunks:
            return "I could not find relevant context in the stored documents."

        return "Based on the retrieved document context: " + chunks[0].text

    async def stream_answer(
        self,
        question: str,
        chunks: list[ChunkResponse],
    ) -> AsyncIterator[str]:
        """Stream answer text in small pieces behind the same generation boundary."""
        answer = await self.generate_answer(question, chunks)

        for word in answer.split():
            yield word + " "
