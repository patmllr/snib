from pathlib import Path
import logging
import typer
import shutil

from .scanner import Scanner
from .utils import handle_include_args, handle_exclude_args, detect_pattern_conflicts, check_include_in_exclude, get_task_choices, get_preset_choices, load_preset
from .config import write_config, load_config, CONFIG_FILE, DEFAULT_CONFIG, DEFAULT_OUTPUT_DIR

logger = logging.getLogger(__name__)
#TODO: using typer.echo instead of logger???

app = typer.Typer(
    help="""snib scans projects and generates prompt-ready chunks.\n
            For help on a specific command, run:\n
                snib COMMAND --help
        """
)

@app.command()
def init(preset: str = typer.Option(None, "--preset", help="Preset to use (feel free to add new ones).", show_choices=True, click_type=get_preset_choices()),
         path: Path = typer.Option(Path.cwd(), "--path", "-p", help="Project directory where snibconfig.toml will be created.")):
    """
    Generates a new snibconfig.toml in your project directory.
    """

    config_path = path / CONFIG_FILE

    if config_path.exists():
        typer.echo(f"{CONFIG_FILE} already exists. No changes made.")
        return

    if preset:
        data = load_preset(preset)
    else:
        data = DEFAULT_CONFIG

    write_config(config_path, data)
    typer.echo(f"{config_path} generated with {(preset + ' preset') if preset else 'defaults'}.")

    #TODO: load config and maybe generate output folder promptready here already

@app.command()
def scan(
    path: Path = typer.Option(None, "--path", "-p", help=f"Path to scan [default: {Path.cwd()}]"),
    description: str = typer.Option(None, "--description", "-d", help="Short project description or changes you want to make [default: empty string]"),
    task: str = typer.Option(None, "--task", "-t", help="Predefined task for AI", case_sensitive=False, show_choices=True, click_type=get_task_choices()),
    include_raw: str = typer.Option("all", "--include", "-i", help="Datatypes or folders/files to included, e.g. *.py, cli.py"),
    exclude_raw: str = typer.Option("", "--exclude", "-e",  help="Datatypes or folders/files to excluded, e.g *.pyc, __pycache__ [default: none]"),
    no_default_exclude: bool = typer.Option(False, "--no-default-excludes", "-E", help="Disable default exclusion"),
    smart: bool = typer.Option(False, "--smart", "-s", help="Smart mode automatically includes only code files and ignores large data/log files"),
    chunk_size: int = typer.Option(None, "--chunk-size", "-c", help="Max number of characters per chunk\nRule of thumb: 1 token ≈ 3-4 chars [default: 30000]"),
    output_dir: Path = typer.Option(None, "--output-dir", "-o", help=f"Folder to save prompt ready data chunks [default: {str(Path.cwd() / 'promptready')}]"),
    force: bool = typer.Option(False, "--force", "-f", help="Force delete existing prompt files and write new ones without validation")     
):
    """
    Scans your project and generates prompt-ready chunks.
    """
    config = DEFAULT_CONFIG
    try:
        config = load_config()
    except FileNotFoundError as e:
        typer.echo(str(e))
        raise typer.Exit(1)

    # combine values: CLI > config 
    path = path or Path(config["project"]["path"])
    description = description or config["project"]["description"]
    task = task or config["instruction"]["task"]

    include_user = handle_include_args(include_raw.split(","))
    exclude_user = handle_exclude_args(exclude_raw.split(","))

    logger.debug(f"User filters after handle_exclude_args: Include: {include_user}, Exclude: {exclude_user}")

    include = include_user or config["filters"]["include"] #TODO: option for config["filters"]["include"] + include_user
    exclude = exclude_user or config["filters"]["exclude"] #TODO: option for config["filters"]["exclude"] + exclude_user

    # add default excludes automatically unless disabled by user
    no_default_exclude = no_default_exclude or config["filters"]["no_default_exclude"]
    if not no_default_exclude:
        exclude = list(set(exclude + config["filters"]["default_exclude"]))
        logger.debug(f"Combined exclude: {exclude}")

    # combine exclude with smart defaults on smart mode enabled
    smart = smart or config["filters"]["smart"]
    if smart:
        include = list(set(include + config["filters"]["smart_include"]))
        exclude = list(set(exclude + config["filters"]["smart_exclude"]))

    # detect filter conflicts (exclude wins) #TODO: set exlude or include wins
    conflicts = detect_pattern_conflicts(include, exclude)
    if conflicts:
        logger.warning(f"Pattern conflicts detected (Exclude wins): {conflicts}")
        # del in include because exlude wins
        include = [p for p in include if not any(p in c for c in conflicts)]

    problematic = check_include_in_exclude(path, include, exclude)
    if problematic:
        logger.warning(f"The following include patterns are inside excluded folders and will be ignored: {problematic}")
        # del in include_patterns because exlude wins
        include = [p for p in include if not any(p in c for c in problematic)]
    
    logger.debug(f"Final include: {include}")
    logger.debug(f"Final exclude: {exclude}")

    chunk_size = chunk_size or config["output"]["chunk_size"]
    output_dir = output_dir or Path(config["output"]["dir"])
    force = force or config["output"]["force"]

    scanner = Scanner(path, config)
    scanner.scan(description, include, exclude, chunk_size, output_dir, force, task)

@app.command()
def clean(
    path: Path = typer.Option(
        Path.cwd(),
        "--path", "-p",
        help="Project directory"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Do not ask for confirmation"
    ),
    config_only: bool = typer.Option(
        False,
        "--config-only",
        help="Only delete the snibconfig.toml file"
    ),
    output_only: bool = typer.Option(
        False,
        "--output-only",
        help="Only delete the promptready folder"
    ),
):
    """
    Removes the promptready folder and/or config file from your project.
    """
    # checks flags conflict
    if config_only and output_only:
        typer.echo("Error: --config-only and --output-only cannot be used together.")
        raise typer.Exit(code=1)

    config_path = path / CONFIG_FILE
    output_dir = path / DEFAULT_OUTPUT_DIR

    to_delete = []

    if config_only:
        if config_path.exists():
            to_delete.append(config_path)
    elif output_only:
        if output_dir.exists():
            to_delete.append(output_dir)
    else:  # default: delete all
        if config_path.exists():
            to_delete.append(config_path)
        if output_dir.exists():
            to_delete.append(output_dir)

    if not to_delete:
        typer.echo("Nothing to clean - no matching files/folders found.")
        raise typer.Exit()

    typer.echo("The following will be deleted:")
    for item in to_delete:
        typer.echo(f"  - {item}")

    if not force:
        confirm = typer.confirm("Do you want to proceed?", default=False)
        if not confirm:
            typer.echo("Aborted.")
            raise typer.Exit()

    for item in to_delete:
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    typer.echo(f"Cleaned project directory {path}")

@app.callback()
def main(verbose: bool = False, dev: bool = False):
    """
    Global options.
    """
    log_level = logging.DEBUG if dev else logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

