import fnmatch
import os
from pathlib import Path

from .chunker import Chunker
from .config import SNIB_PROMPTS_DIR
from .formatter import Formatter
from .logger import logger
from .models import FilterStats, Section
from .utils import build_tree
from .writer import Writer

# TODO: typer progress bar for scan
# HEART OF SNIB


class Scanner:
    def __init__(
        self, path: Path, config: dict
    ):  # TODO: add config to all module classes constructors if needed
        self.path = Path(path).resolve()
        self.config = config

    def _collect_sections(self, description, include, exclude, task) -> list[Section]:

        logger.debug("Collecting sections")

        all_files = [f for f in self.path.rglob("*") if f.is_file()]
        included_files = self._scan_files(self.path, include, exclude)
        excluded_files = [f for f in all_files if f not in included_files]

        include_stats = self._calculate_filter_stats(included_files, "included")
        exclude_stats = self._calculate_filter_stats(excluded_files, "excluded")

        task_dict = self.config["instruction"]["task_dict"]
        instruction = task_dict.get(task, "")

        sections: list[Section] = []

        sections.append(Section(type="description", content=description))
        sections.append(Section(type="task", content=instruction))
        sections.append(
            Section(
                type="filters",
                include=include,
                exclude=exclude,
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

    # ---------------------------------------------------------
    # Helper function: seperate patterns in globs and prefixes
    # ---------------------------------------------------------
    def _split_patterns(self, patterns: list[str]) -> tuple[list[str], list[str]]:
        """
        Seperates patterns in globs und prefixes (directories/files).

        Example:
            "*.py"          -> glob
            "src/snib"      -> prefix
            "utils.py"      -> prefix (direct filename)
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

    # ---------------------------------------------------------
    # Helper function: match directories/filenames vs patterns
    # ---------------------------------------------------------
    def _match_patterns(
        self,
        rel_path: str,
        file_name: str,
        glob_patterns: list[str],
        prefix_patterns: list[str],
    ) -> bool:
        """
        Checks, wether rel_path or filename matches any patterns.

        - Checking glob-patterns for filenames and relative paths.
        - Checking prefix-patterns for:
            - exact relative path
            - beggins with prefix (e.g. "src/snib")
            - exact filename (e.g. "utils.py")
            - exists in path (e.g. "__pycache__")
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

    # ---------------------------------------------------------
    # Helper function: Optimized Scan-Function with os.walk (fast!)
    # ---------------------------------------------------------
    def _scan_files(self, root: Path, includes=None, excludes=None) -> list[Path]:
        """
        Scanns a project directory for files.

        - includes = list of patterns (default: ["*"])
        - excludes = list of patterns (default: [])

        return: list of path objects (filtered).
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
        Calculates FilterStats for a list of files.
        type_label: "included" or "excluded"
        """
        stats = FilterStats(type=type_label)

        for f in files:
            if f.is_file():
                stats.files += 1
                stats.size += f.stat().st_size

        return stats

    def scan(self, description, include, exclude, chunk_size, force, task):

        logger.info(f"Scanning {self.path}")

        sections = self._collect_sections(description, include, exclude, task)
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
                [Section(type="info", content=header)]
            )
            if info_texts:
                chunks_with_header.append(info_texts[0] + chunk)
            else:
                chunks_with_header.append(chunk)

            # chunks_with_header.append(formatter.to_prompt_text([Section(type="info", content=header)])[0] + chunk)

        prompts_dir = self.path / SNIB_PROMPTS_DIR

        writer = Writer(prompts_dir)
        writer.write_chunks(chunks_with_header, force=force)
