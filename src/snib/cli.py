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


@app.command()
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
    Generates a new snibconfig.toml and prompts folder in your project directory.
    """
    pipeline.init(path=path, preset=preset, custom_preset=custom_preset)


@app.command()
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
        help="Choose one of the available tasks to instruct the AI what to do with your project files. [default: None]",
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
        help="Disable default exclusion. Not suggested; also includes e.g. venv, promts, snibconfig.toml, ... [default: False]",
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
    Scans your project and generates prompt-ready chunks.
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


@app.command()
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
    Removes the promts folder and/or snibconfig.toml from your project.
    """
    pipeline.clean(
        path=path, force=force, config_only=config_only, output_only=output_only
    )


@app.callback()
def main(verbose: bool = False):
    """
    Initialising printer.
    """
    set_verbose(verbose)
    if verbose:
        logger.info("Verbose mode enabled.")
