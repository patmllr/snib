import shutil
from pathlib import Path

import typer

from .config import (
    SNIB_CONFIG_FILE,
    SNIB_DEFAULT_CONFIG,
    SNIB_PROMPTS_DIR,
    check_config,
    load_config,
    load_preset,
    write_config,
)
from .logger import logger
from .scanner import Scanner
from .utils import check_include_in_exclude, detect_pattern_conflicts


class SnibPipeline:
    """
    Core pipeline class for initializing, scanning, and cleaning.

    Handles all app.commands:
    - `init`: creates project configuration and prompts folder.
    - `scan`: performs file collection, filtering, and chunking.
    - `clean`: deletes configuration files and/or output folders.
    """

    def init(
        self, path: Path = Path.cwd(), preset: str = None, custom_preset: Path = None
    ):
        """
        Initializes Snib in the given project directory.

        Creates a `snibconfig.toml` using:
        - a built-in default,
        - a named preset, or
        - a custom TOML file.

        Ensures that a `prompts/` folder exists. Skips creation if files/folders already exist.

        Args:
            path (Path, optional): Project directory to initialize. Defaults to current working directory.
            preset (str, optional): Name of a built-in preset to use. Defaults to None.
            custom_preset (Path, optional): Path to a custom preset TOML file. Defaults to None.

        Raises:
            typer.Exit: If both `preset` and `custom_preset` are provided, or if errors occur.
        """

        config_path = path / SNIB_CONFIG_FILE
        prompts_dir = path / SNIB_PROMPTS_DIR

        # check flags conflict
        if preset and custom_preset:
            logger.error("--preset and --custom-preset cannot be used together.")
            raise typer.Exit()

        # check if config already exists else load and write config
        if config_path.exists():
            logger.error(f"{SNIB_CONFIG_FILE} already exists at {config_path}")
            config_exists = True

        else:
            if preset:
                data = load_preset(preset)
            elif custom_preset:
                if not custom_preset.exists():
                    logger.error(f"Custom preset '{custom_preset}' not found.")
                    raise typer.Exit()
                data = load_config(custom_preset)
            else:
                data = SNIB_DEFAULT_CONFIG

            data = check_config(data)  # validate config data
            write_config(config_path, data)
            logger.notice(
                f"{config_path} generated with "
                f"{preset + ' preset.' if preset else 'custom preset: ' + custom_preset.name if custom_preset else 'defaults.'}"
            )
            config_exists = False

        # check if prompts/ folder already exists else create it
        if prompts_dir.exists():
            logger.error(f"{SNIB_PROMPTS_DIR} already exists at {prompts_dir}")
            prompts_dir_exists = True
        else:
            prompts_dir.mkdir(exist_ok=True)
            logger.notice(f"Output folder created at {prompts_dir}")
            prompts_dir_exists = False

        # if something already exists exit
        if config_exists or prompts_dir_exists:
            logger.info("Use 'snib clean' if you want to initialise the project again.")
            raise typer.Exit()

    def scan(
        self,
        path: Path = Path.cwd(),
        description: str = None,
        task: str = None,
        include_raw: str = None,
        exclude_raw: str = None,
        no_default_exclude: bool = False,
        smart: bool = False,
        chunk_size: int = None,
        force: bool = False,
    ):
        """
        Runs the Snib scanning pipeline on the specified project.

        Steps:
        - Load the project configuration (`snibconfig.toml`).
        - Validate presence of output folder.
        - Merge CLI filters with configuration filters.
        - Apply smart include/exclude rules.
        - Detect conflicts between include and exclude patterns.
        - Perform the actual scanning and chunking using the `Scanner`.

        Args:
            path (Path): Project directory.
            description (str): Optional project description or change summary.
            task (str): Optional task name from available AI instructions.
            include_raw (str): Raw comma-separated include patterns.
            exclude_raw (str): Raw comma-separated exclude patterns.
            no_default_exclude (bool): If True, disables default exclusions.
            smart (bool): Enables smart filtering for code files.
            chunk_size (int): Max number of characters per prompt chunk.
            force (bool): Overwrite existing output files without confirmation.

        Raises:
            typer.Exit: If configuration or output folder is missing.
        """

        config_path = path / SNIB_CONFIG_FILE
        output_path = path / SNIB_PROMPTS_DIR

        # check if config and output folder exist in path
        if not config_path.exists():
            logger.error(f"Config file '{config_path}' not found")
            config_missing = True
        else:
            config = load_config(config_path)
            config = check_config(config)  # validate config
            config_missing = False

        if not output_path.exists():
            logger.error(f"Output directory '{output_path}' not found")
            output_missing = True
        else:
            output_missing = False

        # if something is missing exit
        if config_missing or output_missing:
            logger.info("Use 'snib init' first.")
            raise typer.Exit()

        # let the user know which config is used (following keys must exist due to check_config)
        config_name = config["config"]["name"]
        config_author = config["config"]["author"]
        config_version = config["config"]["version"]

        logger.info(
            f"Using {SNIB_CONFIG_FILE}: {config_name} by {config_author} v{config_version}"
        )

        # combine values: CLI > config
        description = description or config["project"]["description"]
        task = task or config["instruction"]["task"]

        # get user includes
        if include_raw:
            include_user = [i.strip() for i in include_raw.split(",") if i.strip()]
            logger.debug(f"User include list: {include_user}")
        else:
            include_user = []
            logger.debug("No user include list specified. (Using 'all')")

        # get user excludes
        if exclude_raw:
            exclude_user = [e.strip() for e in exclude_raw.split(",") if e.strip()]
            logger.debug(f"User exclude list: {exclude_user}")
        else:
            exclude_user = []
            logger.debug("No user exclude list specified.")

        include = include_user or config["filters"]["include"]
        exclude = exclude_user or config["filters"]["exclude"]

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

        # detect include/exclude conflicts (exclude wins)
        conflicts, conflicts_log = detect_pattern_conflicts(include, exclude)
        if conflicts_log:
            logger.warning(
                f"Pattern conflicts detected (Exclude wins): {conflicts_log}"
            )

        if conflicts:
            include = [p for p in include if not any(p in c for c in conflicts)]

        # TODO: this warning currently only works if --exclude "test" and --include "test/file.py" is used
        # this should also work for a implicit path in the --include: --exclude "test" and --include "file.py" if file.py is in test/
        # see Issue #2
        problematic = check_include_in_exclude(path, include, exclude)
        if problematic:
            logger.warning(
                f"The following include patterns are inside excluded folders and will be ignored: {problematic}"
            )
            # logger.debug(f"include before removing problematic: {include}")
            # logger.debug(f"problematic include: {problematic}")
            include = [p for p in include if not any(p in c for c in problematic)]

        logger.debug(f"Final include (passed to Scanner.scan): {include}")
        logger.debug(f"Final exclude (passed to Scanner.scan): {exclude}")

        chunk_size = chunk_size or config["output"]["chunk_size"]
        force = force or config["output"]["force"]

        scanner = Scanner(path, config)
        scanner.scan(description, include, exclude, chunk_size, force, task)

    def clean(self, path: Path, force: bool, config_only: bool, output_only: bool):
        """
        Cleans project by removing the `snibconfig.toml` and/or `prompts` folder.

        Default behavior deletes both config and output folder unless restricted by flags.

        Args:
            path (Path): Project directory.
            force (bool): If True, skips confirmation prompts.
            config_only (bool): If True, only deletes `snibconfig.toml`.
            output_only (bool): If True, only deletes `prompts/` folder.

        Raises:
            typer.Exit: If no files/folders to delete or operation aborted by user.
            typer.Exit: If conflicting flags are provided (`config_only` and `output_only`).
        """

        config_path = path / SNIB_CONFIG_FILE
        output_dir = path / SNIB_PROMPTS_DIR

        # checks flag conflicts
        if config_only and output_only:
            logger.error("--config-only and --output-only cannot be used together.")
            raise typer.Exit()

        to_delete = []

        if config_only:
            if config_path.exists():
                to_delete.append(config_path)
        elif output_only:
            if output_dir.exists():
                to_delete.append(output_dir)
        else:
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
