import os
import time
from pathlib import Path

import pytest

from snib.config import SNIB_DEFAULT_CONFIG
from snib.scanner import Scanner
from snib.utils import check_include_in_exclude, detect_pattern_conflicts


# -------------------------------
# Helper: Build large test projects
# -------------------------------
def create_large_project(root: Path, depth=3, width=5, extra_files=None):
    for d in range(depth):
        for w in range(width):
            folder = root / f"dir{d}_{w}"
            folder.mkdir(parents=True, exist_ok=True)
            for i in range(width):
                (folder / f"file{i}.py").write_text(f"print('file{i}')")
                (folder / f"file{i}.log").write_text("log data")
                (folder / f"file{i}.js").write_text("console.log('hi')")
    if extra_files:
        for path_str, content in extra_files:
            f = root / path_str
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(content)


def normalize_path(p: Path, root: Path):
    """Get relative path with forward slashes for pattern matching."""
    return os.path.relpath(p, root).replace("\\", "/")


# -------------------------------
# Parametrized test for different flag combinations
# -------------------------------
@pytest.mark.parametrize(
    "include,exclude,smart",
    [
        (["*.py"], ["*.log"], True),
        (["*.py", "*.js"], ["*.log"], False),
        ([], [], True),
        (["*.md"], ["dir0_0"], False),
    ],
)
def test_stress_scanner_flags(tmp_path, include, exclude, smart):
    create_large_project(tmp_path, depth=3, width=5)
    scanner = Scanner(tmp_path, config=SNIB_DEFAULT_CONFIG)

    start = time.time()
    sections = scanner._collect_sections(
        description="Stress test project",
        include=include,
        exclude=exclude,
        task="test",
        force=True,
    )
    duration = time.time() - start
    print(
        f"\nScan finished in {duration:.2f}s for include={include}, exclude={exclude}"
    )

    included_files = [
        normalize_path(s.path, scanner.path) for s in sections if s.type == "file"
    ]

    conflicts, conflicts_log = detect_pattern_conflicts(include, exclude)
    problematic = check_include_in_exclude(scanner.path, included_files, exclude)

    assert not conflicts, f"Conflicting patterns detected: {conflicts_log}"
    assert (
        not problematic
    ), f"Some included files are in excluded folders: {problematic}"

    if include:
        for f in included_files:
            assert any(
                f.endswith(p.replace("*", "")) for p in include
            ), f"Included file {f} does not match include pattern"


# -------------------------------
# Edge-case: empty project
# -------------------------------
def test_empty_project(tmp_path):
    scanner = Scanner(tmp_path, config=SNIB_DEFAULT_CONFIG)
    sections = scanner._collect_sections(
        description="Empty project", include=["*"], exclude=[], task="test", force=True
    )

    types = [s.type for s in sections]
    for t in ["description", "task", "filters", "tree"]:
        assert t in types
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
        force=True,
    )

    included_files = [
        normalize_path(s.path, scanner.path) for s in sections if s.type == "file"
    ]
    assert len(included_files) == 0


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
        force=True,
    )

    included_files = [
        normalize_path(s.path, scanner.path) for s in sections if s.type == "file"
    ]

    conflicts, conflicts_log = detect_pattern_conflicts(["*.py"], ["dir0_0/file0.py"])
    problematic = check_include_in_exclude(
        scanner.path, included_files, ["dir0_0/file0.py"]
    )

    assert "dir0_0/file0.py" not in included_files
    assert any(f.endswith("file1.py") for f in included_files)
    assert not conflicts, f"Unexpected conflicts: {conflicts_log}"
    assert not problematic, f"Problematic includes detected: {problematic}"


# PASSED
