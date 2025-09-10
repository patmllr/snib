from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FilterStats:
    """
    Stores statistics about files matched by include/exclude filters.

    Attributes:
        type (str): Type of statistics, e.g., "included" or "excluded".
        files (int): Number of files matching the filter. Defaults to 0.
        size (int): Total size in bytes of all files matching the filter. Defaults to 0.
    """

    type: str
    files: int = 0
    size: int = 0


@dataclass
class Section:
    """
    Represents a section of a project for prompt generation.

    Sections can represent various elements like description, task,
    filtered files, project tree, or individual files.

    Attributes:
        type (str): Section type, e.g., "description", "task", "filters", "tree", "file", "info".
        content (str): The textual content of the section. Defaults to empty string.
        path (Optional[Path]): Path of the file if section represents a file. Defaults to None.
        include (Optional[list[str]]): List of included patterns (for filter sections). Defaults to None.
        exclude (Optional[list[str]]): List of excluded patterns (for filter sections). Defaults to None.
        include_stats (Optional[FilterStats]): Statistics for included files. Defaults to None.
        exclude_stats (Optional[FilterStats]): Statistics for excluded files. Defaults to None.
    """

    type: str
    content: str = ""
    path: Optional[Path] = None
    include: Optional[list[str]] = None
    exclude: Optional[list[str]] = None
    include_stats: Optional[FilterStats] = None
    exclude_stats: Optional[FilterStats] = None
