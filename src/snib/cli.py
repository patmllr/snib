from pathlib import Path

import typer

from .logger import logger, set_verbose
from .pipeline import SnibPipeline
from .utils import get_preset_choices, get_task_choices

pipeline = SnibPipeline()

app = typer.Typer(
    help="""snib scans projects and generates prompt-ready chunks.\n
            For help on a specific command, run:\n
                snib COMMAND --help
        """  # TODO: Add hint on customize snibconfig.toml
)

# TODO: Add @app.command() check to validate a custom.toml


@app.command(help="Generate snibconfig.toml and prompts folder in project directory.")
def init(
    path: Path = typer.Option(
        Path.cwd(),
        "--path",
        "-p",
        help="Project directory to run 'snib init' on.",
    ),
    preset: str = typer.Option(
        None,
        "--preset",
        help="Preset to use. [default: None]",
        show_choices=True,
        click_type=get_preset_choices(),
    ),
    custom_preset: Path = typer.Option(
        None, "--custom-preset", help="Path to a custom preset .toml file."
    ),
):
    """
    Generates snibconfig.toml and prompts folder in a specified project directory.

    Args:
        path (Path): Directory of the project.
        preset (str, optional): Predefined preset to use.
        custom_preset (Path, optional): Path to custom TOML preset.
    """
    pipeline.init(path=path, preset=preset, custom_preset=custom_preset)


@app.command(help="Scans your project and generates prompt-ready chunks.")
def scan(
    path: Path = typer.Option(
        Path.cwd(),
        "--path",
        "-p",
        help=f"Project directory to run 'snib scan' on.",
    ),
    description: str = typer.Option(
        None,
        "--description",
        "-d",
        help="Short project description or changes you want to make. [default: None]",
    ),
    task: str = typer.Option(
        None,
        "--task",
        "-t",
        help="Choose one of the available tasks to instruct the AI. [default: None]",
        case_sensitive=False,
        show_choices=True,
        click_type=get_task_choices(),
    ),
    include_raw: str = typer.Option(
        "all",
        "--include",
        "-i",
        help="Datatypes or folders/files to included, e.g. '*.py, cli.py'",
    ),
    exclude_raw: str = typer.Option(
        "",
        "--exclude",
        "-e",
        help="Datatypes or folders/files to excluded, e.g. '*.pyc, __pycache__' [default: None]",
    ),
    no_default_exclude: bool = typer.Option(
        False,
        "--no-default-excludes",
        "-E",
        help="Disable default exclusion. Not suggested. [default: False]",
    ),
    smart: bool = typer.Option(
        False,
        "--smart",
        "-s",
        help="Smart mode automatically includes only code files and ignores large data/log files. [default: False]",
    ),
    chunk_size: int = typer.Option(
        None,
        "--chunk-size",
        "-c",
        help="Max number of characters per chunk. Rule of thumb: 1 token ≈ 3-4 chars. [default: 30000]",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing prompt files without asking for confirmation. [default: False]",
    ),
):
    """
    Scan the project directory and generate prompt-ready chunks for LLMs.

    Args:
        path (Path): Project directory to scan. Defaults to current working directory.
        description (str, optional): Short description of the project or changes. Defaults to None.
        task (str, optional): Task instruction for the AI. Defaults to None.
        include_raw (str): Comma-separated patterns of files/folders to include. Defaults to "all".
        exclude_raw (str): Comma-separated patterns of files/folders to exclude. Defaults to "".
        no_default_exclude (bool): Disable default exclusions. Defaults to False.
        smart (bool): Enable smart mode to auto-include only relevant code files. Defaults to False.
        chunk_size (int, optional): Maximum number of characters per chunk. Defaults to 30000.
        force (bool): Overwrite existing prompt files without asking. Defaults to False.
    """
    pipeline.scan(
        path=path,
        description=description,
        task=task,
        include_raw=include_raw,
        exclude_raw=exclude_raw,
        no_default_exclude=no_default_exclude,
        smart=smart,
        chunk_size=chunk_size,
        force=force,
    )


@app.command(help="Removes the promts folder and/or snibconfig.toml from your project.")
def clean(
    path: Path = typer.Option(
        Path.cwd(), "--path", "-p", help="Project directory to run 'snib clean' on."
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Do not ask for confirmation."
    ),
    config_only: bool = typer.Option(
        False, "--config-only", help="Only delete the snibconfig.toml file."
    ),
    output_only: bool = typer.Option(
        False, "--output-only", help="Only delete the prompts folder."
    ),
):
    """
    Remove the prompts folder and/or `snibconfig.toml` from the project directory.

    Args:
        path (Path): Project directory. Defaults to current working directory.
        force (bool): Skip confirmation prompt before deletion. Defaults to False.
        config_only (bool): Delete only `snibconfig.toml`. Defaults to False.
        output_only (bool): Delete only the prompts folder. Defaults to False.
    """
    pipeline.clean(
        path=path, force=force, config_only=config_only, output_only=output_only
    )


@app.callback()
def main(verbose: bool = False):
    """
    Initialize the logging and optionally enable verbose mode.

    Args:
        verbose (bool): Enable detailed logging output. Defaults to False.
    """
    set_verbose(verbose)
    if verbose:
        logger.info("Verbose mode enabled.")
