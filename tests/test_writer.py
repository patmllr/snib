from snib.writer import Writer
import pytest

def test_write_and_clear(tmp_path):
    writer = Writer(tmp_path)
    chunks = ["chunk1", "chunk2"]
    files = writer.write_chunks(chunks, force=True, ask_user=False)
    assert len(files) == 2
    for f in files:
        assert f.exists()
    # Clear output
    writer.clear_output()
    assert not any(tmp_path.glob("prompt_*.txt"))
