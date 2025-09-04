import logging
import shutil
from pathlib import Path

import typer

from .config import (
    CONFIG_FILE,
    DEFAULT_CONFIG,
    DEFAULT_OUTPUT_DIR,
    load_config,
    load_preset,
    write_config,
)
from .scanner import Scanner
from .utils import (
    check_include_in_exclude,
    detect_pattern_conflicts,
    handle_exclude_args,
    handle_include_args,
)

logger = logging.getLogger(__name__)


class SnibPipeline:
    def __init__(self, config=None):  # TODO: what comes in here?
        self.config = config

    def init(self, path: Path = Path.cwd(), preset: str = None):
        """Generates a new snibconfig.toml with a preset file or defaults."""
        config_path = path / CONFIG_FILE

        if config_path.exists():
            typer.echo(f"{CONFIG_FILE} already exists. No changes made.")
            return

        if preset:
            data = load_preset(preset)
        else:
            data = DEFAULT_CONFIG

        write_config(config_path, data)
        typer.echo(
            f"{config_path} generated with {(preset + ' preset') if preset else 'defaults'}."
        )

    # TODO: load config and maybe generate output folder promptready here already

    def scan(
        self,
        path: Path,
        description: str,
        task: str,
        include_raw: str,
        exclude_raw: str,
        no_default_exclude: bool,
        smart: bool,
        chunk_size: int,
        output_dir: Path,
        force: bool,
    ):
        """Runs the scanning pipeline"""
        config = DEFAULT_CONFIG  # TODO: del this?
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

        logger.debug(
            f"User filters after handle_exclude_args: Include: {include_user}, Exclude: {exclude_user}"
        )

        include = (
            include_user or config["filters"]["include"]
        )  # TODO: option for config["filters"]["include"] + include_user
        exclude = (
            exclude_user or config["filters"]["exclude"]
        )  # TODO: option for config["filters"]["exclude"] + exclude_user

        # add default excludes automatically unless disabled by user
        no_default_exclude = (
            no_default_exclude or config["filters"]["no_default_exclude"]
        )
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
            logger.warning(
                f"The following include patterns are inside excluded folders and will be ignored: {problematic}"
            )
            # del in include_patterns because exlude wins
            include = [p for p in include if not any(p in c for c in problematic)]

        logger.debug(f"Final include: {include}")
        logger.debug(f"Final exclude: {exclude}")

        chunk_size = chunk_size or config["output"]["chunk_size"]
        output_dir = output_dir or Path(config["output"]["dir"])
        force = force or config["output"]["force"]

        scanner = Scanner(path, config)
        scanner.scan(description, include, exclude, chunk_size, output_dir, force, task)
        ...

    def clean(self, path: Path, force: bool, config_only: bool, output_only: bool):
        """Cleans output folder and/or config file"""
        # checks flags conflict
        if config_only and output_only:
            typer.echo(
                "Error: --config-only and --output-only cannot be used together."
            )
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
