from importlib import resources
from pathlib import Path

import toml

from . import presets  # reference to snib.presets

DEFAULT_CONFIG = {
    "project": {"path": ".", "description": ""},
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
        "include": [],  # TODO: like list
        "exclude": [],  # TODO: like list
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
            "promptready",
            "__pycache__",
            ".git",
            "snibconfig.toml",
        ],
        "no_default_exclude": False,
        "smart": False,
    },
    "output": {
        "dir": "promptready",  # TODO: change to folder_name
        "chunk_size": 30000,
        "force": False,
    },
    "ai": {"model": "gpt-4"},  # TODO: add for later use with APIs
}

CONFIG_FILE = "snibconfig.toml"
DEFAULT_OUTPUT_DIR = "promptready"


def write_config(path: Path = Path(CONFIG_FILE), content: str = DEFAULT_CONFIG):
    """Generates new _config.toml with defaults or presets."""
    if path.exists():
        raise FileExistsError(f"{path} already exists.")
    toml.dump(
        content, path.open("w")
    )  # TODO: Trailing Comma -> clean dump for presets (needs fix) -> tomli-w, tomlkit


def load_config(path: Path = Path(CONFIG_FILE)) -> dict:
    """Loads config files or raises FileNotFoundError if not found."""
    if not path.exists():
        raise FileNotFoundError(f"No {CONFIG_FILE} found. Use 'snib init' first.")
    return toml.load(path.open("r"))


def load_preset(name: str) -> dict:
    preset_file = f"{name}.toml"
    try:
        with resources.open_text(presets, preset_file) as f:
            return toml.load(f)
    except FileNotFoundError:
        raise ValueError(f"Preset '{name}' not found")
