from .logger import logger


class Chunker:
    """
    A utility class to split formatted sections into smaller chunks for processing by LLMs.

    Each chunk will not exceed `chunk_size` characters (including a reserved header space),
    which helps to manage input limits for AI models.
    """

    def __init__(self, chunk_size):
        """
        Initialize a Chunker instance.

        Args:
            chunk_size (int): Maximum character length of each chunk, including header.
        """
        self.chunk_size = chunk_size
        self.header_size = 100  # reserve space for header

    def chunk(self, sections):
        """
        Split a list of formatted sections into chunks of manageable size.

        The method respects the reserved header space and tries to avoid splitting lines in the middle.

        Args:
            sections (list[str]): Formatted sections.

        Returns:
            list[str]: A list of string chunks, each <= `chunk_size` characters including header.
        """
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
