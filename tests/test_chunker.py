import pytest

from snib.chunker import Chunker


def test_chunker_splits_correctly():
    chunker = Chunker(chunk_size=150)
    # every chunk needs at least enough space for header
    if chunker.chunk_size <= chunker.header_size:  # chunker.header_size = 100 (default)
        raise ValueError("chunk_size must be larger than header_size!")
    sections = ["line1\nline2\nline3", "line4\nline5"]
    chunks = chunker.chunk(sections)

    for c in chunks:
        assert len(c) + chunker.header_size <= chunker.chunk_size
    assert "".join(chunks) == "line1\nline2\nline3line4\nline5"


def test_chunker_empty_input():
    chunker = Chunker(chunk_size=50)
    chunks = chunker.chunk([])
    assert chunks == []


# PASSED: pytest tests/test_chunker.py -v
