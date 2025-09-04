import logging
from pathlib import Path

from .utils import format_size

logger = logging.getLogger(__name__)


class Writer:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_chunks(
        self, chunks: list[str], force: bool = False, ask_user: bool = True
    ) -> list[Path]:
        """
        Writes chunks to text files in the output directory.
        - force: overwrite existing files without asking
        - ask_user: prompt user for confirmation (ignored if force=True)
        """

        # TODO: print important msg with typer.echo()

        logger.debug(f"Begin writing {len(chunks)} chunk(s) to {self.output_dir}")

        # Clear existing prompt files if needed
        if any(self.output_dir.glob("prompt_*.txt")):
            if force:
                self.clear_output()
            elif ask_user:
                if (
                    input(
                        f"Output directory '{self.output_dir}' contains prompt file(s). Clear them? [y/N]: "
                    ).lower()
                    == "y"
                ):
                    self.clear_output()

        txt_files = []

        total_size = sum(len(c.encode("utf-8")) for c in chunks)
        size_str = format_size(total_size)

        # Ask before writing
        if not force and ask_user:
            proceed = input(
                f"Do you want to write {len(chunks)} prompt file(s) (total size {size_str}) to '{self.output_dir}'? [y/N]: "
            ).lower()
            if proceed != "y":
                logger.info("User aborted writing prompt files.")
                return []

        for i, chunk in enumerate(chunks, 1):
            filename = self.output_dir / f"prompt_{i}.txt"
            filename.write_text(chunk, encoding="utf-8")
            txt_files.append(filename)

        logger.info(f"Wrote {len(txt_files)} text file(s) to {self.output_dir}")
        return txt_files

    def clear_output(self):
        for file_path in self.output_dir.glob("prompt_*.txt"):
            if file_path.is_file():
                file_path.unlink()
        logger.info(f"Cleared existing prompt file(s) in {self.output_dir}")
