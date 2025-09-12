from importlib import resources
from pathlib import Path

import toml
import typer

from . import presets  # reference to snib.presets
from .logger import logger

SNIB_DEFAULT_CONFIG = {
    "config": {
        "name": "Default snib config",
        "author": "patmllr",
        "version": "1.0",
        "description": "This is a default snib configuration file.",
    },
    "project": {"description": ""},
    "instruction": {
        "task": "",
        "task_dict": {
            "debug": "Debug: Analyze the code and highlight potential errors, bugs, or inconsistencies.",
            "comment": "Comment: Add comments or explain existing functions and code sections.",
            "refactor": "Refactor: Suggest refactorings to make the code cleaner, more readable, and maintainable.",
            "optimize": "Optimize: Improve efficiency or performance of the code.",
            "summarize": "Summarize: Provide a concise summary of the files or modules.",
            "document": "Document: Generate documentation for functions, classes, or modules.",
            "test": "Test: Create unit tests or test cases for the code.",
            "analyze": "Analyze: Perform static analysis or security checks on the code.",
        },
    },
    "filters": {
        "include": [],
        "exclude": [],
        "smart_include": [
            "*.py",
            "*.js",
            "*.ts",
            "*.java",
            "*.cpp",
            "*.c",
            "*.cs",
            "*.go",
            "*.rb",
            "*.php",
            "*.html",
            "*.css",
            "*.scss",
            "*.less",
            "*.json",
            "*.yaml",
            "*.yml",
            "*.xml",
            "*.sh",
            "*.bat",
            "*.ps1",
            "*.pl",
            "*.swift",
            "*.kt",
            "*.m",
            "*.r",
            "*.sql",
        ],
        "smart_exclude": [
            "*.log",
            "*.zip",
            "*.tar",
            "*.gz",
            "*.bin",
            "*.exe",
            "*.dll",
            "*.csv",
        ],
        "default_exclude": [
            "venv",
            "prompts",
            "__pycache__",
            ".git",
            "snibconfig.toml",
        ],
        "no_default_exclude": False,
        "smart": False,
        "warning_include_limit": 100,
    },
    "output": {
        "chunk_size": 30000,
        "force": False,
    },
}

SNIB_CONFIG_FILE = "snibconfig.toml"
SNIB_PROMPTS_DIR = "prompts"


def write_config(
    path: Path = Path(SNIB_CONFIG_FILE), content: str = SNIB_DEFAULT_CONFIG
):
    """
    Write a new snib configuration file in TOML format.

    If the file already exists, raises a FileExistsError.

    Args:
        path (Path, optional): Path to write the config file. Defaults to SNIB_CONFIG_FILE.
        content (dict, optional): Dictionary representing the configuration. Defaults to SNIB_DEFAULT_CONFIG.

    Raises:
        FileExistsError: If the config file already exists.
    """
    if path.exists():
        raise FileExistsError(f"{path} already exists.")
    # TODO: Trailing Comma -> clean dump for presets (needs fix)
    toml.dump(content, path.open("w"))


def load_config(path: Path = Path(SNIB_CONFIG_FILE)) -> dict:
    """
    Load a snib configuration from a TOML file.

    Args:
        path (Path, optional): Path to the config file. Defaults to SNIB_CONFIG_FILE.

    Returns:
        dict | None: Loaded configuration dictionary or None if the file does not exist.
    """
    if not path.exists():
        return None
    return toml.load(path.open("r"))


def load_preset(name: str) -> dict:
    """
    Load a preset configuration from the built-in `presets`.

    Args:
        name (str): Name of the preset (without '.toml').

    Returns:
        dict: Preset configuration dictionary.

    Raises:
        ValueError: If the preset file does not exist in the `presets`.
    """
    preset_file = f"{name}.toml"
    try:
        with resources.open_text(presets, preset_file) as f:
            return toml.load(f)
    except FileNotFoundError:
        raise ValueError(f"Preset '{name}' not found")


def check_config(config: dict) -> dict:
    """
    Validate a Snib config dictionary.

    - Ensure required sections and keys exist.

    Args:
        config (dict): config file.

    Returns:
        dict: Validated config.

    typer.Exit is called on fatal errors.
    """
    mandatory_sections = list(SNIB_DEFAULT_CONFIG.keys())
    missing_sections = [sec for sec in mandatory_sections if sec not in config]

    if missing_sections:
        logger.error(
            f"Broken config: Missing {missing_sections} section(s) in snibconfig.toml."
        )
        logger.notice(
            "Run 'snib clean' and 'snib init' to generate a new config or edit properly."
        )
        raise typer.Exit()

    optional_subsections = ["warning_include_limit", "task_dict"]
    missing_subsections = []
    for sec, defaults in SNIB_DEFAULT_CONFIG.items():
        for sub in defaults.keys():
            if sub in optional_subsections:
                continue
            if sub not in config.get(sec, {}):
                missing_subsections.append(f"{sec}.{sub}")

    if missing_subsections:
        logger.error(
            f"Broken config: Missing {missing_subsections} key(s) in snibconfig.toml."
        )
        logger.notice(
            "Run 'snib clean' and 'snib init' to generate a new config or edit properly."
        )
        raise typer.Exit()

    return config
