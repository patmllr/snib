import fnmatch
from importlib import resources
from pathlib import Path

import toml
from click import Choice

from . import presets  # reference to snib.presets
from .config import SNIB_DEFAULT_CONFIG, load_config
from .logger import logger


def handle_include_args(include_list):
    include_list = [i.strip() for i in include_list if i.strip()]

    if include_list and include_list[0].lower() != "all":
        logger.debug(f"User include list: {include_list}")
    else:
        include_list = []
        logger.debug("No user include list or 'all' specified.")

    return include_list


def handle_exclude_args(exclude_list):
    exclude_list = [e.strip() for e in exclude_list if e.strip()]

    if exclude_list:
        logger.debug(f"User exclude list: {exclude_list}")
    else:
        logger.debug("No user exclude list specified.")

    return exclude_list


def build_tree(
    path: Path, include: list[str], exclude: list[str], prefix: str = ""
) -> list[str]:
    """
    Builds a tree representation of the directory with include/exclude filters.
    - Directories are only shown if they contain at least one valid file.
    - Files are only shown if they match the include patterns (or if include is empty = allow all).
    """
    ELBOW = "└──"
    TEE = "├──"
    PIPE_PREFIX = "│   "
    SPACE_PREFIX = "    "

    """
    def should_include_file(entry: Path) -> bool:
        if any(entry.match(p) or entry.name == p for p in exclude):
            return False
        if entry.is_file():
            return not include or any(entry.match(p) or entry.name == p for p in include)
        return True  # dirs -> first yes, then check later
    """

    def should_include_file(entry: Path) -> bool:
        # excluded?
        if any(entry.match(p) or entry.name == p for p in exclude):
            return False

        # only files, if include empty or match
        if entry.is_file():
            return not include or any(
                entry.match(p) or entry.name == p or p in entry.parts for p in include
            )

        # folder: show if
        #    - include emptry or
        #    - foldername itself in or
        #    - any file below matches include
        if entry.is_dir():
            if not include or entry.name in include:
                return True
            # min. one file below matches include
            return any(
                f.match(p) or f.name == p
                for p in include
                for f in entry.rglob("*")
                if f.is_file()
            )

        return True

    lines = [path.name] if not prefix else []
    entries = [
        e
        for e in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        if should_include_file(e)
    ]

    for i, entry in enumerate(entries):
        connector = ELBOW if i == len(entries) - 1 else TEE
        line = f"{prefix}{connector} {entry.name}"

        if entry.is_dir():
            extension = SPACE_PREFIX if i == len(entries) - 1 else PIPE_PREFIX
            subtree = build_tree(entry, include, exclude, prefix + extension)
            if len(subtree) > 0:  # only append if not empty
                lines.append(line)
                lines.extend(subtree)
        else:
            lines.append(line)

    return lines


def format_size(size: int) -> str:
    """Return human-readable size string."""
    if size >= 1024**2:
        return f"{size / (1024**2):.2f} MB"
    elif size >= 1024:
        return f"{size / 1024:.2f} KB"
    return f"{size} B"


def detect_pattern_conflicts(includes: list[str], excludes: list[str]) -> set[str]:
    conflicts = set()
    # check each include against each exclude
    for inc in includes:
        for exc in excludes:
            # exact match
            if inc == exc:
                conflicts.add(inc)
            # include eaten by exclude
            elif fnmatch.fnmatch(inc, exc):
                conflicts.add(f"{inc} (matched by {exc})")
            # exclude is more specific than include -> overwritten
            elif fnmatch.fnmatch(exc, inc):
                conflicts.add(f"{inc} (conflicts with {exc})")
    return conflicts


def check_include_in_exclude(
    path: Path, includes: list[str], excludes: list[str]
) -> list[str]:
    """
    Checks whether include patterns contain files that are located in an exclude folder.
    Returns the problematic includes.
    """
    problematic = []

    for inc in includes:
        inc_path = path / inc
        if not inc_path.exists():
            continue
        for exc in excludes:
            exc_path = path / exc
            # only check folders
            if exc_path.is_dir() and exc_path in inc_path.parents:
                problematic.append(inc)
    return problematic


def get_task_choices() -> list[str]:
    config = load_config()
    if not config:
        config = SNIB_DEFAULT_CONFIG
    return Choice(list(config["instruction"]["task_dict"].keys()))


def get_preset_choices() -> list[str]:
    """Return available preset names without extension."""
    try:
        files = resources.files(presets).iterdir()
        return Choice(
            [f.name.rsplit(".", 1)[0] for f in files if f.name.endswith(".toml")]
        )
    except FileNotFoundError:
        # if package is not installed right
        return []
