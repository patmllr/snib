# Snib ✂️

**Snib** is a Python CLI tool to scan your projects, collect source files, and generate **prompt-ready chunks** for use with large language models (LLMs). It helps you prepare clean, structured context from your codebase with include/exclude filters, project trees, and chunking. It supports filtering by file types, folders, regex and can optionally run in **smart mode** to automatically ignore large logs or binary files.

## 🚀 Features 

- Scan entire projects recursively.
- Include or exclude files/folders with globs or explicit paths.
- Generate prompt-ready chunks with configurable size.
- Built-in tasks: `debug`, `comment`, `refactor`, `optimize`, `summarize`, `document`, `test`, `analyze`.
- Smart mode automatically focuses on source code and ignores unnecessary files.
- Detects conflicts between include/exclude patterns.
- Logs scanning and processing details at INFO or DEBUG level.
- Clean and organized prompt output for large projects.
- Uses three commands `init`, `scan` and `clean`.

---

## 📦 Installation 

```bash
pip install https://github.com/patmllr/snib/releases/latest/download/snib-0.3.0-py3-none-any.whl
```

Alternatively download the latest wheel here: [Latest Release](https://github.com/patmllr/snib/releases/latest)

### 🧰 Recommended setup

Create a Python virtual environment inside your project folder and install `snib` in the `venv`:

```bash
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
source venv/bin/activate       # Linux / macOS
pip install https://github.com/patmllr/snib/releases/latest/download/snib-0.3.0-py3-none-any.whl
```

## ⚡ CLI Usage

`snib` scans projects and generates prompt-ready chunks.

```bash
snib [OPTIONS] COMMAND [ARGS]...
```

### ⚙️ Global Options

| Option                     | Description                              |
| -------------------------- | ---------------------------------------- |
| `--verbose / --no-verbose` | Show INFO logs (default: `--no-verbose`) |
| `--dev / --no-dev`         | Show DEBUG logs (default: `--no-dev`)    |
| `--install-completion`     | Install shell completion                 |
| `--show-completion`        | Show completion script                   |
| `--help`                   | Show this message and exit               |

### 📦 Commands

`init`

Generates a new `snibconfig.toml` in your project directory.

| Option        | Short | Description                                           |
| ------------- | ----- | ----------------------------------------------------- |
| `--preset`    |       | Preset to use: `unity`, `unreal` (extendable)         |
| `--path PATH` | `-p`  | Target directory (default: current working directory) |
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
| `--output-dir PATH`     | `-o`  | Output folder (default: `promptready`)                                                                  |
| `--force`               | `-f`  | Force overwrite existing prompt files                                                                   |
| `--help`                |       | Show this message and exit                                                                              |

`clean`

Removes the `promptready` folder and/or config file from your project.

| Option          | Short | Description                                    |
| --------------- | ----- | ---------------------------------------------- |
| `--path PATH`   | `-p`  | Project directory (default: current directory) |
| `--force`       | `-f`  | Do not ask for confirmation                    |
| `--config-only` |       | Only delete `snibconfig.toml`                  |
| `--output-only` |       | Only delete the `promptready` folder           |
| `--help`        |       | Show this message and exit                     |

## 👍 Rule of Thumb for Chunk Sizes

Since snib chunks by characters, the following guidelines can help to estimate the chunk size:

| Model / LLM           | Max Context (Tokens) | Recommended `--chunk-size` (Chars) | Notes                                      |
| --------------------- | -------------------- | ---------------------------------- | ------------------------------------------ |
| LLaMA 2 (7B/13B)      | 4,000                | 12,000 – 14,000                    | 1 token ≈ 3–4 chars                        |
| Mistral 7B            | 8,000                | 28,000                             | Leave a safety margin                      |
| GPT-4 classic         | 8,000                | 28,000                             |                                            |
| GPT-4-32k             | 32,000               | 110,000                            |                                            |
| GPT-4o / GPT-5 (128k) | 128,000              | 450,000 – 500,000                  | Very large models, massive chunks possible |

## 🎮 Presets

Snib comes with ready-to-use presets:

- `unity.toml` → Configured for Unity projects (*.cs, *.shader, …)
- `unreal.toml` → Configured for Unreal projects (extendable)

You can create your own presets by adding new .toml files to the presets directory.

## 🗂️ Example 

```bash
snib init

snib --verbose scan -e "dist, junk" --chunk-size 100000 --smart
```

```text
#[INFO]
Please do not give output until all prompt files are sent. Prompt file 1/4

#[DESCRIPTION]
This is a demo.

#[TASK]
Debug: Analyze the code and highlight potential errors, bugs, or inconsistencies.

#[INCLUDE/EXCLUDE]
Include patterns: ['*.py']
Exclude patterns: ['promptready', 'dist', 'junk', 'venv', '__pycache__']
Included files: files: 16, total size: 28.86 KB
Excluded files: files: 1943, total size: 262.11 MB

#[PROJECT TREE]
snib
├── src
│   └── snib
│       ├── __init__.py
│       ├── __main__.py
│       ├── ...
│       └── writer.py
└── tests
    ├── test_chunker.py
    ├── ...
    └── test_writer.py

#[FILE] tests\test_chunker.py
import pytest
from snib.chunker import Chunker

...

#[INFO]
Prompt file 4/4

...
```

After running snib, a `promptready` folder is generated with prompt files ready to get copied to the clipboard:

```text
prompt_1.txt
...
prompt_4.txt
```

## 🧠 Best Practices

- Always install snib inside a virtual environment.
- `venv` and `promptready` are automatically excluded from scans.
- Use `--smart` to focus on code and avoid unnecessary large files.
- Adjust `--chunk-size` based on your target LLM and the table above.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add new feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

## 📝 Notes

- Snib is designed to be lightweight and easily integrated into CI/CD pipelines.
- Works cross-platform (Windows, Linux, macOS).
- Automatically inserts headers in multi-chunk outputs to guide LLM processing.

## 📜 License

MIT License © 2025 Patrick Müller