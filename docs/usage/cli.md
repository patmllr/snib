# CLI Usage

```bash
snib [OPTIONS] COMMAND [ARGS]...
```

## Global Options

| Option                     | Description                              |
| -------------------------- | ---------------------------------------- |
| `--verbose / --no-verbose` | Show INFO logs (default: `--no-verbose`) |
| `--install-completion`     | Install shell completion                 |
| `--show-completion`        | Show completion script                   |
| `--help`                   | Show this message and exit               |

## Commands

`init`

Generates a new `prompts` folder and `snibconfig.toml` in your project directory.

| Option        | Short | Description                                           |
| ------------- | ----- | ----------------------------------------------------- |
| `--path PATH` | `-p`  | Target directory (default: current directory)         |
| `--preset`    |       | Preset to use: `unity`, `unreal` (extendable)         |
| `--help`      |       | Show this message and exit                            |

`scan`

Scans your project and generates prompt-ready chunks.

| Option                  | Short | Description                                                                                             |
| ----------------------- | ----- | ------------------------------------------------------------------------------------------------------- |
| `--path PATH`           | `-p`  | Path to scan (default: current directory)                                                               |
| `--description TEXT`    | `-d`  | Short project description or changes you want to make                                                   |
| `--task`                | `-t`  | Predefined task: `debug`, `comment`, `refactor`, `optimize`, `summarize`, `document`, `test`, `analyze` |
| `--include TEXT`        | `-i`  | File types or folders to include, e.g., `*.py, cli.py`                                                  |
| `--exclude TEXT`        | `-e`  | File types or folders to exclude, e.g., `*.pyc, __pycache__`                                            |
| `--no-default-excludes` | `-E`  | Disable automatic exclusion of `venv`, `promptready`, `__pycache__`                                     |
| `--smart`               | `-s`  | Smart mode: only code files, ignores logs/large files                                                   |
| `--chunk-size INT`      | `-c`  | Max characters per chunk (default: 30,000)                                                              |
| `--force`               | `-f`  | Force overwrite existing prompt files                                                                   |
| `--help`                |       | Show this message and exit                                                                              |

`clean`

Removes the `prompts` folder and/or `sinibconfig.toml` from your project directory.

| Option          | Short | Description                                    |
| --------------- | ----- | ---------------------------------------------- |
| `--path PATH`   | `-p`  | Project directory (default: current directory) |
| `--force`       | `-f`  | Do not ask for confirmation                    |
| `--config-only` |       | Only delete `snibconfig.toml`                  |
| `--output-only` |       | Only delete the `promptready` folder           |
| `--help`        |       | Show this message and exit                     |