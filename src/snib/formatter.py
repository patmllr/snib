from .logger import logger
from .models import FilterStats, Section
from .utils import format_size


class Formatter:
    def to_prompt_text(self, sections: list[Section]) -> list[str]:
        logger.debug("Converting sections to promptready text")
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
        Formats FilterStats readably with format_size()
        Shows number of files and total size in B/KB/MB.
        """
        return f"files: {stats.files}, total size: {format_size(stats.size)}"
