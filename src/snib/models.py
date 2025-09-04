from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FilterStats:
    type: str
    files: int = 0
    size: int = 0


@dataclass
class Section:
    type: str
    content: str = ""
    path: Optional[Path] = None
    include: Optional[list[str]] = None
    exclude: Optional[list[str]] = None
    include_stats: Optional[FilterStats] = None
    exclude_stats: Optional[FilterStats] = None
