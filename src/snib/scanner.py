import fnmatch
import os
from pathlib import Path

import typer

from .chunker import Chunker
from .config import SNIB_PROMPTS_DIR
from .formatter import Formatter
from .logger import logger
from .models import FilterStats, Section
from .utils import build_tree, format_size
from .writer import Writer

# TODO: typer progress bar for scan
# HEART OF SNIB


class Scanner:
    """
    The core scanning engine of Snib.

    The Scanner traverses a project directory, applies include/exclude
    filters, builds structured `Section` objects, and prepares them
    for formatting and chunking into prompt-ready text.

    It integrates with:
    - `Formatter` (to structure prompt text)
    - `Chunker` (to split large outputs into chunks)
    - `Writer` (to persist prompt files to disk)

    Attributes:
        path (Path): Root project directory to scan.
        config (dict): Parsed configuration dictionary (from `snibconfig.toml`).
    """

    def __init__(self, path: Path, config: dict):
        """
        Initialize a Scanner instance.

        Args:
            path (Path): Project root directory.
            config (dict): Snib configuration dictionary.
        """
        # TODO: add config to all module classes constructors if needed
        self.path = Path(path).resolve()
        self.config = config
        self.include_warning_num_files = (
            100  # warn if > 100 files included TODO: mby add this to config?
        )

    def _collect_sections(
        self, description, include, exclude, force, task
    ) -> list[Section]:
        """
        Collects structured project sections for prompt generation.

        This includes:
        - Project description
        - Task instruction (from config)
        - Filter summary (include/exclude patterns and stats)
        - Project tree
        - Individual file contents (included files only)

        Args:
            description (str): Project description text.
            include (list[str]): Include patterns (globs/prefixes).
            exclude (list[str]): Exclude patterns (globs/prefixes).
            task (str): Task key (looked up in `task_dict` in config).

        Returns:
            list[Section]: A list of `Section` objects representing
                different parts of the project.
        """
        logger.debug("Collecting sections")

        all_files = [f for f in self.path.rglob("*") if f.is_file()]
        included_files = self._scan_files(self.path, include, exclude)
        excluded_files = [f for f in all_files if f not in included_files]

        include_stats = self._calculate_filter_stats(included_files, "included")
        exclude_stats = self._calculate_filter_stats(excluded_files, "excluded")

        # let the user know what was included/excluded
        logger.info(
            f"Included stats: Files: {include_stats.files}, Size: {format_size(include_stats.size)}"
        )
        logger.info(
            f"Excluded stats: Files: {exclude_stats.files}, Size: {format_size(exclude_stats.size)}"
        )

        # warn the user if he includes alot of files, e.g > 100
        if include_stats.files > self.include_warning_num_files:
            logger.warning(
                f"Included files exceed {self.include_warning_num_files}. This may lead to large prompts and increased costs."
            )
            logger.notice("Consider refining your include/exclude patterns.")
            if not force:
                confirm = logger.confirm("Do you want to proceed?", default=False)
                if not confirm:
                    logger.info("Aborted.")
                    raise typer.Exit()

        task_dict = self.config["instruction"]["task_dict"]
        instruction = task_dict.get(task, "")

        sections: list[Section] = []

        sections.append(Section(type="description", content=description))
        sections.append(Section(type="task", content=instruction))
        sections.append(
            Section(
                type="filters",
                include=include,  # TODO: included_files ?
                exclude=exclude,  # TODO: excluded_files ?
                include_stats=include_stats,
                exclude_stats=exclude_stats,
            )
        )
        sections.append(
            Section(
                type="tree",
                content="\n".join(
                    build_tree(path=self.path, include=include, exclude=exclude)
                ),
            )
        )

        for file_path in included_files:
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                content = f"<Could not read {file_path.name}>\n"
            sections.append(
                Section(
                    type="file", path=file_path.relative_to(self.path), content=content
                )
            )

        logger.debug(f"Collected {len(sections)} sections")

        return sections

    def _split_patterns(self, patterns: list[str]) -> tuple[list[str], list[str]]:
        """
        Splits patterns into glob patterns and prefix patterns.

        Examples:
            "*.py"     -> glob
            "src/snib" -> prefix
            "utils.py" -> prefix (exact filename)

        Args:
            patterns (list[str]): List of pattern strings.

        Returns:
            tuple[list[str], list[str]]:
                - globs: Glob-style patterns (with `*`, `?`).
                - prefixes: Exact filenames or directory prefixes.
        """
        globs = []
        prefixes = []
        for p in patterns:
            p = str(p).replace("\\", "/").rstrip("/")  # normalise Windows/Linux
            if "*" in p or "?" in p:
                globs.append(p)
            else:
                prefixes.append(p)
        return globs, prefixes

    def _match_patterns(
        self,
        rel_path: str,
        file_name: str,
        glob_patterns: list[str],
        prefix_patterns: list[str],
    ) -> bool:
        """
        Checks whether a relative path or filename matches any patterns.

        Matching logic:
        - Glob patterns are matched against filenames and full relative paths.
        - Prefix patterns are matched against:
            * Exact relative path
            * Path starting with prefix (e.g. "src/snib")
            * Exact filename (e.g. "utils.py")
            * Path parts containing prefix (e.g. `__pycache__`).

        Args:
            rel_path (str): Relative path from project root.
            file_name (str): Filename only.
            glob_patterns (list[str]): Patterns with wildcards.
            prefix_patterns (list[str]): Exact path or filename prefixes.

        Returns:
            bool: True if path matches any pattern, else False.
        """
        # glob check
        for g in glob_patterns:
            if fnmatch.fnmatch(file_name, g) or fnmatch.fnmatch(rel_path, g):
                return True

        # prefix check
        for p in prefix_patterns:
            if (
                rel_path == p
                or rel_path.startswith(p + "/")
                or file_name == p
                or f"/{p}/"
                in f"/{rel_path}/"  # folders or path parts somewhere in path
                # or fnmatch.fnmatch(rel_path, p)  # flexible matching works for: utils.py, /src/snib/utils.py, **/utils.py
            ):
                return True

        return False

    def _scan_files(self, root: Path, includes=None, excludes=None) -> list[Path]:
        """
        Scans the project directory for files using include/exclude filters.

        - Uses `os.walk` for efficient traversal.
        - Excludes whole directories early for speed.
        - Applies both glob and prefix matching.

        Args:
            root (Path): Root directory to scan.
            includes (list[str] | None): Include patterns (default: `["*"]`).
            excludes (list[str] | None): Exclude patterns (default: `[]`).

        Returns:
            list[Path]: List of included file paths.
        """
        includes = includes or ["*"]
        excludes = excludes or []

        include_globs, include_prefixes = self._split_patterns(includes)
        exclude_globs, exclude_prefixes = self._split_patterns(excludes)

        results = []

        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = Path(dirpath).relative_to(root).as_posix()

            # --- Step 1: exclude whole directories early (Speed!)
            # going through list and deleting excluded directories from `dirnames`.
            dirnames[:] = [
                d
                for d in dirnames
                if not self._match_patterns(
                    f"{rel_dir}/{d}" if rel_dir != "." else d,
                    d,
                    exclude_globs,
                    exclude_prefixes,
                )
            ]

            # --- Step 2: Check files
            for fname in filenames:
                rel_path = (
                    f"{rel_dir}/{fname}" if rel_dir != "." else fname
                )  # relative path from root

                # Exclude check
                if self._match_patterns(
                    rel_path, fname, exclude_globs, exclude_prefixes
                ):
                    continue

                # Include check
                if self._match_patterns(
                    rel_path, fname, include_globs, include_prefixes
                ):
                    results.append(Path(dirpath) / fname)

        return results

    def _calculate_filter_stats(
        self, files: list[Path], type_label: str
    ) -> FilterStats:
        """
        Calculates file statistics for a filter set.

        Args:
            files (list[Path]): Files to analyze.
            type_label (str): Either `"included"` or `"excluded"`.

        Returns:
            FilterStats: Number of files and total size in bytes.
        """
        stats = FilterStats(type=type_label)

        for f in files:
            if f.is_file():
                stats.files += 1
                stats.size += f.stat().st_size

        return stats

    def scan(self, description, include, exclude, chunk_size, force, task):
        """
        Executes the scanning pipeline.

        Workflow:
        1. Collects project sections (`_collect_sections`).
        2. Formats them into prompt-ready text (`Formatter`).
        3. Splits into chunks (`Chunker`).
        4. Prepends headers for multi-file prompts.
        5. Writes results into `prompts` (`Writer`).

        Args:
            description (str): Project description text.
            include (list[str]): Include patterns.
            exclude (list[str]): Exclude patterns.
            chunk_size (int): Maximum chunk size (characters).
            force (bool): If True, overwrite existing outputs.
            task (str): Task key for instructions.

        Returns:
            None: Results are written to disk in `prompts`.
        """
        logger.info(f"Scanning {self.path}")

        sections = self._collect_sections(description, include, exclude, force, task)
        formatter = Formatter()
        formatted = formatter.to_prompt_text(sections)

        chunker = Chunker(chunk_size)
        chunks = chunker.chunk(formatted)

        # leave headspace for header 100 chars in chunker -> self.header_size
        # insert header on first lines of every chunk

        chunks_with_header = []

        total = len(chunks)
        for i, chunk in enumerate(chunks, 1):
            if total <= 1:
                header = ""
            else:
                header = (
                    f"Please do not give output until all prompt files are sent. Prompt file {i}/{total}\n"
                    if i == 1
                    else f"Prompt file {i}/{total}\n"
                )

            # works with empty info section
            info_texts = formatter.to_prompt_text(
                [
                    Section(type="info", content=header)
                ]  # this executes to_prompt_text i times!
            )
            if info_texts:
                chunks_with_header.append(info_texts[0] + chunk)
            else:
                chunks_with_header.append(chunk)

            # chunks_with_header.append(formatter.to_prompt_text([Section(type="info", content=header)])[0] + chunk)

        prompts_dir = self.path / SNIB_PROMPTS_DIR

        writer = Writer(prompts_dir)
        writer.write_chunks(chunks_with_header, force=force)
