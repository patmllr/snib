from .logger import logger
from .models import FilterStats, Section
from .utils import format_size


class Formatter:
    """
    Formatter converts project sections into prompt-ready text.

    This class processes a list of Section objects (info, description, task,
    filters, project tree, file contents) and formats them into text blocks
    suitable for AI prompting. It also provides helper functions to format
    statistics about included/excluded files.
    """

    def to_prompt_text(self, sections: list[Section]) -> list[str]:
        """
        Convert a list of Section objects into a list of prompt-ready strings.

        Each section type is formatted differently:
        - info: general information about the project
        - description: project description
        - task: AI task instructions
        - filters: included/excluded patterns with statistics
        - tree: project folder tree
        - file: actual file content with path header

        Args:
            sections (list[Section]): A list of Section objects representing
                different parts of the project scan.

        Returns:
            list[str]: A list of formatted strings, each representing a
                section. (This gets passed to the chunker.)

        Notes:
            - INFO, DESCRIPTION and TASK sections are skipped if empty.
        """
        logger.debug("Converting sections to prompt-ready text")
        texts = []
        for s in sections:
            if s.type == "info":
                if s.content:
                    texts.append(f"#[INFO]\n{s.content}\n")
                else:
                    logger.info("Only one prompt file; skipping INFO section.")
            elif s.type == "description":
                if s.content:
                    texts.append(f"#[DESCRIPTION]\n{s.content}\n\n")
                else:
                    logger.info(
                        "No description provided; skipping DESCRIPTION section."
                    )
            elif s.type == "task":
                if s.content:
                    texts.append(f"#[TASK]\n{s.content}\n\n")
                else:
                    logger.info("No task specified; skipping TASK section.")
            elif s.type == "filters":
                include_text = s.include if s.include else ""
                exclude_text = s.exclude if s.exclude else ""
                include_stats_text = (
                    self._format_stats(s.include_stats) if s.include_stats else ""
                )
                exclude_stats_text = (
                    self._format_stats(s.exclude_stats) if s.exclude_stats else ""
                )

                texts.append(
                    f"#[INCLUDE/EXCLUDE]\n"
                    f"Include patterns: {include_text}\n"
                    f"Exclude patterns: {exclude_text}\n"
                    f"Included files: {include_stats_text}\n"
                    f"Excluded files: {exclude_stats_text}\n\n"
                )
            elif s.type == "tree":
                texts.append(f"#[PROJECT TREE]\n{s.content}\n\n")
            elif s.type == "file":
                texts.append(f"#[FILE] {s.path}\n{s.content}\n\n")
        return texts

    def _format_stats(self, stats: FilterStats) -> str:
        """
        Format FilterStats for human-readable output.

        Shows number of files and total size using readable units. (B/KB/MB/GB)

        Args:
            stats (FilterStats): Statistics object containing file count
                and total size in bytes.

        Returns:
            str: Formatted string, e.g. "files: 10, total size: 2.5 MB".
        """
        return f"files: {stats.files}, total size: {format_size(stats.size)}"
