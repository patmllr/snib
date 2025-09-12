import os
from pathlib import Path

import pytest

from snib.config import SNIB_DEFAULT_CONFIG
from snib.models import FilterStats, Section
from snib.scanner import Scanner


@pytest.fixture
def config_dict():
    """Return a copy of the default config so tests always pass check_config."""
    import copy

    return copy.deepcopy(SNIB_DEFAULT_CONFIG)


@pytest.fixture
def sample_project(tmp_path):
    """Creates a sample project directory with nested files."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("print('a')")
    (tmp_path / "src" / "b.txt").write_text("b file")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("assert True")
    return tmp_path


# ------------------
# Unit tests
# ------------------


def test_split_patterns(config_dict):
    s = Scanner(Path("."), config_dict)
    globs, prefixes = s._split_patterns(["*.py", "src", "file.txt"])
    assert "*.py" in globs
    assert "src" in prefixes
    assert "file.txt" in prefixes


def test_match_patterns_glob_and_prefix(config_dict):
    s = Scanner(Path("."), config_dict)
    globs, prefixes = ["*.py"], ["src"]
    assert s._match_patterns("src/a.py", "a.py", globs, prefixes)
    assert not s._match_patterns("docs/readme.md", "readme.md", globs, prefixes)


def test_scan_files_includes_and_excludes(sample_project, config_dict):
    s = Scanner(sample_project, config_dict)
    files = s._scan_files(sample_project, includes=["*.py"], excludes=["tests"])
    rels = [f.relative_to(sample_project).as_posix() for f in files]
    assert "src/a.py" in rels
    assert "tests/test_a.py" not in rels


def test_calculate_filter_stats_counts(tmp_path, config_dict):
    f = tmp_path / "x.txt"
    f.write_text("hello")
    s = Scanner(tmp_path, config_dict)
    stats = s._calculate_filter_stats([f], "included")
    assert isinstance(stats, FilterStats)
    assert stats.files == 1
    assert stats.size == len("hello")


# ------------------
# Integration-style tests
# ------------------


def test_collect_sections_builds_sections(sample_project, config_dict):
    s = Scanner(sample_project, config_dict)
    sections = s._collect_sections(
        description="desc",
        include=["*.py"],
        exclude=["tests"],
        force=True,
        task=list(config_dict["instruction"]["task_dict"].keys())[0],
    )
    types = [sec.type for sec in sections]
    assert "description" in types
    assert "task" in types
    assert "filters" in types
    assert "tree" in types
    assert any(sec.type == "file" for sec in sections)


def test_scan_pipeline_writes_chunks(monkeypatch, sample_project, config_dict):
    s = Scanner(sample_project, config_dict)

    # Monkeypatch Formatter, Chunker, Writer to avoid heavy I/O
    class DummyFormatter:
        def to_prompt_text(self, sections):
            return ["formatted"]

    class DummyChunker:
        def __init__(self, size):
            pass

        def chunk(self, formatted):
            return ["chunk1", "chunk2"]

    written = {}

    class DummyWriter:
        def __init__(self, outdir):
            self.outdir = outdir

        def write_chunks(self, chunks, force):
            written["chunks"] = chunks
            return [Path("f1"), Path("f2")]

    monkeypatch.setattr("snib.scanner.Formatter", DummyFormatter)
    monkeypatch.setattr("snib.scanner.Chunker", DummyChunker)
    monkeypatch.setattr("snib.scanner.Writer", DummyWriter)

    s.scan(
        description="desc",
        include=["*.py"],
        exclude=["tests"],
        chunk_size=1000,
        force=True,
        task=list(config_dict["instruction"]["task_dict"].keys())[0],
    )

    assert "chunks" in written
    assert any("Prompt file" in c or "chunk" in c for c in written["chunks"])


# PASSED
