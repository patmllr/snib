import pytest

from snib.utils import (
    build_tree,
    check_include_in_exclude,
    detect_pattern_conflicts,
    handle_exclude_args,
    handle_include_args,
)


def test_handle_include_exclude_args():
    assert handle_include_args([".py", " "]) == [".py"]
    assert handle_include_args(["all"]) == []
    assert handle_exclude_args([".log", ""]) == [".log"]


def test_detect_pattern_conflicts_basic():
    includes = ["*.py", "*.js"]
    excludes = ["*.py", "*.txt"]
    conflicts = detect_pattern_conflicts(includes, excludes)
    assert "*.py" in conflicts


def test_check_include_in_exclude(tmp_path):
    inc_file = tmp_path / "include.txt"
    inc_file.write_text("hello")
    exc_dir = tmp_path / "exclude_dir"
    exc_dir.mkdir()
    problem = check_include_in_exclude(tmp_path, ["include.txt"], ["exclude_dir"])
    assert problem == []


def test_build_tree(tmp_path):
    (tmp_path / "a").mkdir()
    f1 = tmp_path / "a" / "file1.py"
    f1.write_text("print('hi')")
    tree = build_tree(tmp_path, include=["*.py"], exclude=[])
    tree_str = "\n".join(tree)
    assert "file1.py" in tree_str


# PASSED pytest tests/test_utils.py -v
