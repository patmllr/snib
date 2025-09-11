import fnmatch
from importlib import resources
from pathlib import Path

import toml
from click import Choice

from . import presets  # reference to snib.presets
from .config import SNIB_DEFAULT_CONFIG, load_config
from .logger import logger


def handle_include_args(include_list):
    """
    Normalize and validate include arguments.

    - Strips whitespace from all patterns.
    - Removes empty entries.
    - Treats `"all"` (case-insensitive) as "no restrictions" -> returns empty list.

    Args:
        include_list (list[str]): Raw include patterns from CLI or config.

    Returns:
        list[str]: Cleaned include patterns, or empty if `"all"` or nothing specified.
    """
    include_list = [i.strip() for i in include_list if i.strip()]

    if include_list and include_list[0].lower() != "all":
        logger.debug(f"User include list: {include_list}")
    else:
        include_list = []
        logger.debug("No user include list or 'all' specified.")

    return include_list


def handle_exclude_args(exclude_list):
    """
    Normalize and validate exclude arguments.

    - Strips whitespace from all patterns.
    - Removes empty entries.

    Args:
        exclude_list (list[str]): Raw exclude patterns from CLI or config.

    Returns:
        list[str]: Cleaned exclude patterns.
    """
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
    Build a visual tree representation of a project directory.

    Filtering rules:
    - Excluded entries are never shown.
    - Files are shown if they match include patterns (or if include is empty).
    - Directories are shown if:
        * They are explicitly included, or
        * They contain at least one valid file inside.

    Args:
        path (Path): Root directory to scan.
        include (list[str]): Include patterns (globs, filenames, or dirs).
        exclude (list[str]): Exclude patterns (globs, filenames, or dirs).
        prefix (str, optional): Current tree indentation prefix. Defaults to "".

    Returns:
        list[str]: List of formatted strings representing the directory tree.
    """
    ELBOW = "└──"
    TEE = "├──"
    PIPE_PREFIX = "│   "
    SPACE_PREFIX = "    "

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
    """
    Convert a byte size into a human-readable string.

    Examples:
        >>> format_size(500)
        '500 B'
        >>> format_size(2048)
        '2.00 KB'
        >>> format_size(5_242_880)
        '5.00 MB'

    Args:
        size (int): File size in bytes.

    Returns:
        str: Human-readable string (B, KB, MB).
    """
    # TODO: add GB
    if size >= 1024**2:
        return f"{size / (1024**2):.2f} MB"
    elif size >= 1024:
        return f"{size / 1024:.2f} KB"
    return f"{size} B"


def detect_pattern_conflicts(includes: list[str], excludes: list[str]) -> set[str]:
    """
    Detect conflicts between include and exclude patterns.

    Cases:
    - Exact match (include == exclude).
    - Include pattern matched by exclude.
    - Exclude pattern more specific than include.

    Args:
        includes (list[str]): List of include patterns.
        excludes (list[str]): List of exclude patterns.

    Returns:
        set[str]: Conflicting include patterns with explanations.
    """

    conflicts = set()
    conflicts_log = set()
    # check each include against each exclude
    for inc in includes:
        for exc in excludes:
            # exact match is a conflict
            if inc == exc:
                conflicts.add(inc)
                conflicts_log.add(f"{inc} == {exc}")
            # include eaten by exclude -> fnmatch.fnmatch("*.py", "utils.py") -> False
            elif fnmatch.fnmatch(inc, exc):
                conflicts.add(inc)
                conflicts_log.add(f"{inc} (matched by {exc})")
            # exclude is more specific than include -> fnmatch.fnmatch("utils.py", "*.py") -> True DONT ADD TO CONFLICTS!
            elif fnmatch.fnmatch(exc, inc):
                conflicts_log.add(f"{inc} (conflicts with {exc})")

    return conflicts, conflicts_log


def check_include_in_exclude(
    path: Path, includes: list[str], excludes: list[str]
) -> list[str]:
    """
    Check whether include patterns fall inside excluded directories.

    For example:
        includes = ["src/main.py"]
        excludes = ["src"]
        → "src/main.py" is problematic.

    Args:
        path (Path): Root directory of the project.
        includes (list[str]): Include patterns (file paths).
        excludes (list[str]): Exclude patterns (dir paths).

    Returns:
        list[str]: List of problematic include patterns.
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
    """
    Retrieve available task keys from config.

    - Reads tasks from `snibconfig.toml` if available.
    - Falls back to default config otherwise.

    Returns:
        list[str]: Available task keys (for CLI autocompletion).
    """
    config = load_config()
    if not config:
        config = SNIB_DEFAULT_CONFIG
    return Choice(list(config["instruction"]["task_dict"].keys()))


def get_preset_choices() -> list[str]:
    """
    Retrieve available preset names.

    - Scans the `snib.presets` package for `.toml` files.
    - Strips file extensions.

    Returns:
        list[str]: Preset names without extension (for CLI autocompletion).
    """
    try:
        files = resources.files(presets).iterdir()
        return Choice(
            [f.name.rsplit(".", 1)[0] for f in files if f.name.endswith(".toml")]
        )
    except FileNotFoundError:
        # if package is not installed right
        return []
