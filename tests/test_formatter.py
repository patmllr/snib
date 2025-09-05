from pathlib import Path

from snib.formatter import Formatter
from snib.models import FilterStats, Section


def test_formatter_output_sections():
    formatter = Formatter()
    sections = [
        Section(type="info", content="Info text"),
        Section(type="description", content="Desc text"),
        Section(type="task", content="Task text"),
        Section(
            type="filters",
            include=["*.py"],
            exclude=["*.log"],
            include_stats=FilterStats("included", 2, 2048),
            exclude_stats=FilterStats("excluded", 1, 1024),
        ),
        Section(type="tree", content="project_tree"),
        Section(type="file", path=Path("example.py"), content="print('hello')"),
    ]
    texts = formatter.to_prompt_text(sections)
    combined = "\n".join(texts)
    assert "Info text" in combined
    assert "Desc text" in combined
    assert "Task text" in combined
    assert "example.py" in combined


def test_formatter_size_formatting():
    formatter = Formatter()
    stats = FilterStats(type="included", files=1, size=500)
    assert "500 B" in formatter._format_stats(stats)
    stats.size = 2048
    assert "2.00 KB" in formatter._format_stats(stats)
    stats.size = 5 * 1024**2
    assert "5.00 MB" in formatter._format_stats(stats)


# PASSED pytest tests/test_formatter.py
