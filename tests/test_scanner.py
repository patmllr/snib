import pytest

from snib.scanner import Scanner


def test_file_matches_filters(tmp_path):
    file_a = tmp_path / "a.py"
    file_a.write_text("print('a')")
    file_b = tmp_path / "b.log"
    file_b.write_text("log")

    scanner = Scanner(tmp_path)
    # TODO: Scanner.__init__() missing 1 required positional argument: 'config'
    assert scanner._file_matches_filters(file_a, include=["*.py"], exclude=["*.log"])
    assert not scanner._file_matches_filters(
        file_b, include=["*.py"], exclude=["*.log"]
    )


def test_get_included_files(tmp_path):
    (tmp_path / "a.py").write_text("print('a')")
    (tmp_path / "b.log").write_text("log")
    scanner = Scanner(tmp_path)
    files = scanner._get_included_files(tmp_path, include=["*.py"], exclude=["*.log"])
    assert len(files) == 1
    assert files[0].name == "a.py"


# FAILED tests/test_scanner.py::test_file_matches_filters - TypeError: Scanner.__init__() missing 1 required positional argument: 'config'
