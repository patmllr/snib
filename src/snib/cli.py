import logging
from pathlib import Path

import typer

from .pipeline import SnibPipeline
from .utils import get_preset_choices, get_task_choices

logger = logging.getLogger(__name__)
pipeline = SnibPipeline()

app = typer.Typer(
    help="""snib scans projects and generates prompt-ready chunks.\n
            For help on a specific command, run:\n
                snib COMMAND --help
        """
)


@app.command()
def init(
    path: Path = typer.Option(
        Path.cwd(),
        "--path",
        "-p",
        help="Project directory where snibconfig.toml will be created.",
    ),
    preset: str = typer.Option(
        None,
        "--preset",
        help="Preset to use (feel free to add new ones).",
        show_choices=True,
        click_type=get_preset_choices(),
    ),
):
    """
    Generates a new snibconfig.toml in your project directory.
    """
    pipeline.init(path=path, preset=preset)


@app.command()
def scan(
    path: Path = typer.Option(
        None, "--path", "-p", help=f"Path to scan [default: {Path.cwd()}]"
    ),
    description: str = typer.Option(
        None,
        "--description",
        "-d",
        help="Short project description or changes you want to make [default: empty string]",
    ),
    task: str = typer.Option(
        None,
        "--task",
        "-t",
        help="Predefined task for AI",
        case_sensitive=False,
        show_choices=True,
        click_type=get_task_choices(),
    ),
    include_raw: str = typer.Option(
        "all",
        "--include",
        "-i",
        help="Datatypes or folders/files to included, e.g. *.py, cli.py",
    ),
    exclude_raw: str = typer.Option(
        "",
        "--exclude",
        "-e",
        help="Datatypes or folders/files to excluded, e.g *.pyc, __pycache__ [default: none]",
    ),
    no_default_exclude: bool = typer.Option(
        False, "--no-default-excludes", "-E", help="Disable default exclusion"
    ),
    smart: bool = typer.Option(
        False,
        "--smart",
        "-s",
        help="Smart mode automatically includes only code files and ignores large data/log files",
    ),
    chunk_size: int = typer.Option(
        None,
        "--chunk-size",
        "-c",
        help="Max number of characters per chunk\nRule of thumb: 1 token ≈ 3-4 chars [default: 30000]",
    ),
    output_dir: Path = typer.Option(
        None,
        "--output-dir",
        "-o",
        help=f"Folder to save prompt ready data chunks [default: {str(Path.cwd() / 'promptready')}]",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force delete existing prompt files and write new ones without validation",
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
        output_dir=output_dir,
        force=force,
    )


@app.command()
def clean(
    path: Path = typer.Option(Path.cwd(), "--path", "-p", help="Project directory"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Do not ask for confirmation"
    ),
    config_only: bool = typer.Option(
        False, "--config-only", help="Only delete the snibconfig.toml file"
    ),
    output_only: bool = typer.Option(
        False, "--output-only", help="Only delete the promptready folder"
    ),
):
    """
    Removes the promptready folder and/or config file from your project.
    """
    pipeline.clean(
        path=path, force=force, config_only=config_only, output_only=output_only
    )


@app.callback()
def main(verbose: bool = False, dev: bool = False):
    """
    Global options.
    """
    log_level = logging.DEBUG if dev else logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=log_level, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
