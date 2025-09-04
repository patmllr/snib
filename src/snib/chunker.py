from .logger import logger


class Chunker:
    def __init__(self, chunk_size):
        self.chunk_size = chunk_size
        self.header_size = 100  # reserve space for header

    def chunk(self, sections):

        logger.info(
            f"Using chunk_size={self.chunk_size} chars "
            f"(≈ {self.chunk_size // 4}-{self.chunk_size // 3} tokens estimated)"
        )

        chunks = []
        current_chunk = ""
        for section in sections:
            lines = section.splitlines(keepends=True)
            for line in lines:
                if len(current_chunk) + len(line) + self.header_size > self.chunk_size:
                    chunks.append(current_chunk)
                    current_chunk = ""
                current_chunk += line
        if current_chunk:
            chunks.append(current_chunk)

        logger.info(f"Created {len(chunks)} chunk(s)")

        return chunks
