from pathlib import Path

import pytest

from snib.utils import build_tree, check_include_in_exclude, detect_pattern_conflicts


# -------------------------------
# Include/exclude handling replaced
# -------------------------------
def test_include_exclude_patterns_normalization(tmp_path):
    includes = ["*.py", "src/utils"]
    excludes = ["*.log", "src/utils"]

    # Create files and folders to match the patterns
    (tmp_path / "src/utils").mkdir(parents=True)
    file_included = tmp_path / "src/utils/file.py"
    file_included.write_text("print('hi')")
    file_other = tmp_path / "main.py"
    file_other.write_text("print('main')")

    # detect conflicts
    conflicts, conflicts_log = detect_pattern_conflicts(includes, excludes)

    # Now conflicts should include "src/utils" because it's in both include & exclude
    assert conflicts == {"src/utils"}

    # check_include_in_exclude should detect actual files inside excluded dirs
    included_files = ["src/utils/file.py", "main.py"]
    problematic = check_include_in_exclude(tmp_path, included_files, ["src/utils"])
    assert "src/utils/file.py" in problematic
    assert "main.py" not in problematic


# -------------------------------
# build_tree tests
# -------------------------------
def test_build_tree_basic(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    f1 = tmp_path / "a" / "file1.py"
    f2 = tmp_path / "b" / "file2.js"
    f1.write_text("print('hi')")
    f2.write_text("console.log('hi')")

    # Only include *.py
    tree = build_tree(tmp_path, include=["*.py"], exclude=[])
    tree_str = "\n".join(tree)
    assert "file1.py" in tree_str
    assert "file2.js" not in tree_str

    # Include all
    tree_all = build_tree(tmp_path, include=[], exclude=[])
    tree_all_str = "\n".join(tree_all)
    assert "file1.py" in tree_all_str
    assert "file2.js" in tree_all_str

    # Exclude b folder
    tree_excl = build_tree(tmp_path, include=[], exclude=["b"])
    tree_excl_str = "\n".join(tree_excl)
    assert "file1.py" in tree_excl_str
    assert "file2.js" not in tree_excl_str


# -------------------------------
# Edge case: empty project
# -------------------------------
def test_empty_project_build_tree(tmp_path):
    tree = build_tree(tmp_path, include=["*"], exclude=[])
    assert tree == [tmp_path.name]


# -------------------------------
# Check include inside excluded dir
# -------------------------------
def test_check_include_inside_excluded_dir(tmp_path):
    (tmp_path / "exclude").mkdir()
    f = tmp_path / "exclude" / "file.py"
    f.write_text("print('hi')")
    problematic = check_include_in_exclude(tmp_path, ["exclude/file.py"], ["exclude"])
    assert problematic == ["exclude/file.py"]


# PASSED
