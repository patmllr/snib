from pathlib import Path

import typer

from .logger import logger
from .utils import format_size


class Writer:
    """
    Handles writing prompt chunks to disk and managing output files.

    This class is responsible for:
    - Ensuring the output directory exists.
    - Writing prompt chunks into sequentially numbered `.txt` files.
    - Optionally clearing existing prompt files before writing.
    """

    def __init__(self, output_dir: str):
        """
        Initialize a Writer.

        Args:
            output_dir (str): Path to the output directory where prompt files
                should be stored. The directory is created if it does not exist.
        """
        # TODO: fix this section
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_chunks(self, chunks: list[str], force: bool = False) -> list[Path]:
        """
        Write prompt chunks to text files.

        Behavior:
        - Existing files named `prompt_*.txt` are cleared if `force=True`.
        - If `force=False` and prompt files already exist, the user is asked
          for confirmation before overwriting.
        - Files are written as `prompt_1.txt`, `prompt_2.txt`, etc.
        - Each file contains one chunk of text.

        Args:
            chunks (list[str]): List of text chunks to be written.
            force (bool, optional): Overwrite existing files without confirmation.
                Defaults to False.

        Returns:
            list[Path]: List of paths to the written text files.

        Raises:
            typer.Exit: If the user aborts when prompted for confirmation.
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
        """
        Delete all existing prompt files (`prompt_*.txt`) in the output directory.

        - This is typically called before writing new chunks.
        - Only files matching the pattern `prompt_*.txt` are removed.
        """
        for file_path in self.output_dir.glob("prompt_*.txt"):
            if file_path.is_file():
                file_path.unlink()
