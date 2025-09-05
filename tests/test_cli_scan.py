from pathlib import Path

import pytest

from snib.chunker import Chunker
from snib.formatter import Formatter
from snib.models import Section
from snib.scanner import Scanner
from snib.writer import Writer


def test_end_to_end_scan(tmp_path):
    # -------------------------------
    # Setup fake project files
    # -------------------------------
    # Create folders and files
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "file1.py").write_text("print('hello')")
    (tmp_path / "src" / "file2.js").write_text("console.log('hi')")
    (tmp_path / "README.md").write_text("# Project README")
    (tmp_path / "ignore.log").write_text("This should be ignored")

    # -------------------------------
    # Initialize Scanner
    # -------------------------------
    scanner = Scanner(tmp_path)
    # TODO: Scanner.__init__() missing 1 required positional argument: 'config'

    include_patterns = ["*.py", "*.js"]
    exclude_patterns = ["*.log"]

    sections = scanner._collect_sections(
        description="Test project",
        include=include_patterns,
        exclude=exclude_patterns,
        task="test",
    )

    # Check sections collected
    section_types = [s.type for s in sections]
    assert "description" in section_types
    assert "task" in section_types
    assert "filters" in section_types
    assert "tree" in section_types
    assert any(s.type == "file" for s in sections)

    # -------------------------------
    # Formatter
    # -------------------------------
    formatter = Formatter()
    formatted_texts = formatter.to_prompt_text(sections)
    combined_text = "\n".join(formatted_texts)
    assert "Test project" in combined_text
    assert "file1.py" in combined_text
    assert "file2.js" in combined_text
    assert "ignore.log" not in combined_text

    # -------------------------------
    # Chunker
    # -------------------------------
    chunker = Chunker(chunk_size=200)  # small chunk for testing
    chunks = chunker.chunk(formatted_texts)
    assert len(chunks) >= 1
    for c in chunks:
        assert len(c) + chunker.header_size <= 200

    # -------------------------------
    # Writer
    # -------------------------------
    output_dir = tmp_path / "output"
    writer = Writer(output_dir)
    written_files = writer.write_chunks(chunks, force=True, ask_user=False)
    assert all(f.exists() for f in written_files)
    assert len(written_files) == len(chunks)

    # Clear output and check
    writer.clear_output()
    assert not any(output_dir.glob("prompt_*.txt"))


# FAILED tests/test_cli_scan.py::test_end_to_end_scan - TypeError: Scanner.__init__() missing 1 required positional argument: 'config'
