import shutil
from pathlib import Path

import typer

from .config import (
    SNIB_CONFIG_FILE,
    SNIB_DEFAULT_CONFIG,
    SNIB_PROMPTS_DIR,
    load_config,
    load_preset,
    write_config,
)
from .logger import logger
from .scanner import Scanner
from .utils import (
    check_include_in_exclude,
    detect_pattern_conflicts,
    handle_exclude_args,
    handle_include_args,
)


class SnibPipeline:
    def __init__(self, config=None):  # TODO: what comes in here?
        self.config = config

    def init(
        self, path: Path = Path.cwd(), preset: str = None, custom_preset: Path = None
    ):
        """
        Initialize snib in the given project directory.

        - Creates a `snibconfig.toml` configuration file using either:
            * a specified preset, or
            * a custom.toml file, or
            * the built-in default config.
        - Ensures that a `prompts/` output directory exists alongside the config.
        - If both already exist, initialization is skipped to avoid overwriting.
        """
        config_path = path / SNIB_CONFIG_FILE
        prompts_dir = path / SNIB_PROMPTS_DIR

        # check flags conflict
        if preset and custom_preset:
            logger.error("--preset and --custom-preset cannot be used together.")
            raise typer.Exit(1)

        if config_path.exists():
            logger.warning(f"{SNIB_CONFIG_FILE} already exists at {config_path}")
            config_exists_warn = True

        else:
            config_exists_warn = False
            if preset:
                data = load_preset(preset)
            elif custom_preset:
                if not custom_preset.exists():
                    logger.error(f"Custom preset '{custom_preset}' not found.")
                    raise typer.Exit(1)
                data = load_config(custom_preset)
            else:
                data = SNIB_DEFAULT_CONFIG
            # data = load_preset(preset) if preset else SNIB_DEFAULT_CONFIG
            write_config(config_path, data)
            logger.notice(
                f"{config_path} generated with "
                f"{preset + ' preset' if preset else custom_preset.name if custom_preset else 'defaults'}"
            )

        if prompts_dir.exists():
            prompts_dir_exists_warn = True
            logger.warning(f"{SNIB_PROMPTS_DIR} already exists at {prompts_dir}")
        else:
            prompts_dir_exists_warn = False
            prompts_dir.mkdir(exist_ok=True)
            logger.notice(f"Output folder created at {prompts_dir}")

        if config_exists_warn or prompts_dir_exists_warn:
            logger.info(
                "Use 'snib clean' first if you want to initialise your project again."
            )

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
        force: bool,
    ):
        """Runs the scanning pipeline"""
        # config = SNIB_DEFAULT_CONFIG  # TODO: del this?
        config_path = path / SNIB_CONFIG_FILE
        output_path = path / SNIB_PROMPTS_DIR

        config_missing = False
        output_missing = False

        if not config_path.exists():
            logger.error(f"Config file '{config_path}' not found")
            config_missing = True
        else:
            config = load_config(config_path)

        if not output_path.exists():
            logger.error(f"Output directory '{output_path}' not found")
            output_missing = True

        # if something is missing exit
        if config_missing or output_missing:
            logger.info("Use 'snib init' first")  # TODO: change to note/hint
            raise typer.Exit(1)

        # config exists made sure ...
        # combine values: CLI > config
        config_description = config["config"]["description"]
        config_author = config["config"]["author"]
        config_version = config["config"]["version"]

        # TODO: better formatting + more infos in config.py, e.g name, ...
        # TODO: coloring 4 community
        logger.info(
            f"Using 'snibconfig.toml': {config_description} by {config_author} v{config_version}"
        )

        path = path or Path(config["project"]["path"])  # TODO: check this
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
        force = force or config["output"]["force"]

        scanner = Scanner(path, config)
        scanner.scan(description, include, exclude, chunk_size, force, task)

    def clean(self, path: Path, force: bool, config_only: bool, output_only: bool):
        """Cleans output folder and/or config file"""
        # checks flags conflict
        if config_only and output_only:
            logger.error("--config-only and --output-only cannot be used together.")
            raise typer.Exit(code=1)

        config_path = path / SNIB_CONFIG_FILE
        output_dir = path / SNIB_PROMPTS_DIR

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
            logger.info("Nothing to clean. No matching files/folders found.")
            raise typer.Exit()

        logger.info("The following will be deleted:")
        for item in to_delete:
            logger.info(f"- {item}")

        if not force:
            confirm = logger.confirm("Do you want to proceed?", default=False)
            if not confirm:
                logger.info("Aborted.")
                raise typer.Exit()

        for item in to_delete:
            if item.is_dir():
                shutil.rmtree(item)
                logger.notice(f"Deleted: {item}")
            else:
                item.unlink()
                logger.notice(f"Deleted: {item}")
