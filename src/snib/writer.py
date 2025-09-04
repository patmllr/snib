from pathlib import Path

import typer

from .logger import logger
from .utils import format_size


class Writer:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_chunks(self, chunks: list[str], force: bool = False) -> list[Path]:
        """
        Writes chunks to text files in the output directory.
        - force: overwrite existing files without asking
        - ask_user: prompt user for confirmation (ignored if force=True)
        """

        logger.debug(f"Begin writing {len(chunks)} chunk(s) to {self.output_dir}")

        # Clear existing prompt files if needed
        prompt_files = list(self.output_dir.glob("prompt_*.txt"))
        if prompt_files:
            count = len(prompt_files)
            if force:
                self.clear_output()
                logger.notice(
                    f"Cleared {count} existing prompt file(s) in '{self.output_dir}'."
                )
            else:
                confirm = logger.confirm(
                    f"'{self.output_dir}' already contains {count} prompt file(s). Clear them?",
                    default=False,
                )
                if not confirm:
                    logger.info("Aborted.")
                    raise typer.Exit()

                self.clear_output()
                logger.notice(
                    f"Cleared {count} existing prompt file(s) in '{self.output_dir}'."
                )

        txt_files = []

        total_size = sum(len(c.encode("utf-8")) for c in chunks)
        size_str = format_size(total_size)

        # Ask before writing
        if not force:
            confirm = logger.confirm(
                f"Do you want to write {len(chunks)} prompt file(s) (total size {size_str}) to '{self.output_dir}'?",
                default=False,
            )
            if not confirm:
                logger.info("Aborted.")
                raise typer.Exit()

        for i, chunk in enumerate(chunks, 1):
            filename = self.output_dir / f"prompt_{i}.txt"
            filename.write_text(chunk, encoding="utf-8")
            txt_files.append(filename)

        logger.notice(f"Wrote {len(txt_files)} text file(s) to {self.output_dir}")
        return txt_files

    def clear_output(self):
        for file_path in self.output_dir.glob("prompt_*.txt"):
            if file_path.is_file():
                file_path.unlink()
