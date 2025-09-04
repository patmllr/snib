import fnmatch
from pathlib import Path

from .chunker import Chunker
from .config import SNIB_PROMPTS_DIR
from .formatter import Formatter
from .logger import logger
from .models import FilterStats, Section
from .utils import build_tree
from .writer import Writer

# TODO: typer progress bar for scan


class Scanner:
    def __init__(
        self, path: Path, config: dict
    ):  # TODO: add config to all module classes constructors if needed
        self.path = Path(path).resolve()
        self.config = config

    def _collect_sections(self, description, include, exclude, task) -> list[Section]:

        logger.debug("Collecting sections")

        # included_files = self._get_included_files(self.path, include, exclude)
        # excluded_files = self._get_included_files(self.path, exclude, include)
        all_files = [f for f in self.path.rglob("*") if f.is_file()]
        included_files = self._get_included_files(self.path, include, exclude)
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

        for file_path in self._get_included_files(self.path, include, exclude):
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

    # V1 BUGGED _file_matches_filters, _get_included_files

    def _file_matches_filters(
        self, path: Path, include: list[str], exclude: list[str]
    ) -> bool:
        for pattern in exclude:
            # check full path vs glob + filename correct + foldernames check
            if path.match(pattern) or path.name == pattern or pattern in path.parts:
                return False

        if include:
            for pattern in include:
                # same here
                if path.match(pattern) or path.name == pattern or pattern in path.parts:
                    return True

            return False  # nothing matched

        # default: if no include -> allow all
        return True

    def _get_included_files(
        self, path: Path, include: list[str], exclude: list[str]
    ) -> list[Path]:
        matching_files = []

        for file in path.rglob("*"):
            if not file.is_file():
                continue
            if self._file_matches_filters(path=file, include=include, exclude=exclude):
                matching_files.append(file)

        for file in matching_files:
            logger.debug(f"MATCHING: {file}")

        return matching_files

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
