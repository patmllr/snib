import time
from pathlib import Path

import pytest

from snib.config import SNIB_DEFAULT_CONFIG
from snib.scanner import Scanner


# -------------------------------
# Helper: Build large test projects
# -------------------------------
def create_large_project(root: Path, depth=3, width=5, extra_files=None):
    """
    Create a virtual project tree.
    - depth: folder depth
    - width: number of folders/files per level
    - extra_files: list of (relative_path, content) to add specific files
    """
    for d in range(depth):
        for w in range(width):
            folder = root / f"dir{d}_{w}"
            folder.mkdir(parents=True, exist_ok=True)
            for i in range(width):
                # Python files
                (folder / f"file{i}.py").write_text(f"print('file{i}')")
                # Log files
                (folder / f"file{i}.log").write_text("log data")
                # JS files
                (folder / f"file{i}.js").write_text("console.log('hi')")
    # Extra custom files
    if extra_files:
        for path_str, content in extra_files:
            f = root / path_str
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(content)


# -------------------------------
# Parametrized test for different flag combinations
# -------------------------------
@pytest.mark.parametrize(
    "include,exclude,smart",
    [
        (["*.py"], ["*.log"], True),
        (["*.py", "*.js"], ["*.log"], False),
        ([], [], True),  # include all
        (["*.md"], ["dir0_0"], False),  # some edge case
    ],
)
def test_stress_scanner_flags(tmp_path, include, exclude, smart):
    # Build project
    create_large_project(tmp_path, depth=3, width=5)

    # Initialize scanner
    scanner = Scanner(tmp_path, config=SNIB_DEFAULT_CONFIG)

    # Measure performance
    start = time.time()
    sections = scanner._collect_sections(
        description="Stress test project",
        include=include,
        exclude=exclude,
        task="test",
    )
    duration = time.time() - start
    print(
        f"\nScan finished in {duration:.2f}s for include={include}, exclude={exclude}"
    )

    # -------------------------------
    # Assertions: check filters
    # -------------------------------
    included_files = [s.path.name for s in sections if s.type == "file"]
    for f in included_files:
        for ex in exclude:
            assert ex not in f, f"Excluded file {f} was included"
        # Only include matching files
        if include:
            assert any(
                [f.endswith(p.replace("*", "")) for p in include]
            ), f"Included file {f} does not match include pattern"


# -------------------------------
# Edge-case: empty project
# -------------------------------
def test_empty_project(tmp_path):
    scanner = Scanner(tmp_path, config=SNIB_DEFAULT_CONFIG)
    sections = scanner._collect_sections(
        description="Empty project",
        include=["*"],
        exclude=[],
        task="test",
    )
    # Only description, task, filters, tree sections expected
    types = [s.type for s in sections]
    for t in ["description", "task", "filters", "tree"]:
        assert t in types
    # No files
    assert all(s.type != "file" for s in sections)


# -------------------------------
# Edge-case: all files excluded
# -------------------------------
def test_all_files_excluded(tmp_path):
    create_large_project(tmp_path, depth=2, width=2)
    scanner = Scanner(tmp_path, config=SNIB_DEFAULT_CONFIG)
    sections = scanner._collect_sections(
        description="All excluded",
        include=["*"],
        exclude=["*"],
        task="test",
    )
    # No files should be included
    files = [s for s in sections if s.type == "file"]
    assert len(files) == 0


# -------------------------------
# Edge-case: conflicting patterns
# -------------------------------
def test_conflicting_patterns(tmp_path):
    create_large_project(tmp_path, depth=1, width=2)
    scanner = Scanner(tmp_path, config=SNIB_DEFAULT_CONFIG)
    sections = scanner._collect_sections(
        description="Conflicts",
        include=["*.py"],
        exclude=["dir0_0/file0.py"],
        task="test",
    )
    included_files = [s.path.name for s in sections if s.type == "file"]
    print(included_files)
    assert (
        "file0.py" not in included_files
    )  # TODO: Fix this bug 'file0.py' is excluded!
    assert "file1.py" in included_files


# pytest tests/test_stress_scan.py -v
