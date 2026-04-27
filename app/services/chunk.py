class ChunkService:
    def split_text_into_chunks(self, text: str) -> list[str]:
        parts = [part.strip() for part in text.split("\n\n")]
        return [part for part in parts if part]
