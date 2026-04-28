from app.models.api import ChunkResponse


class ChatService:
    async def generate_answer(self, question: str, chunks: list[ChunkResponse]) -> str:
        """Generate an answer from retrieved chunks behind a replaceable service boundary."""
        if not chunks:
            return "I could not find relevant context in the stored documents."

        return "Based on the retrieved document context: " + chunks[0].text
