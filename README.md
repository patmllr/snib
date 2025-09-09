# Snib ✂️

**Snib** is a Python CLI tool to scan your projects and generate prompt-ready chunks for use with LLMs.

## 💡 Why Snib?

Today there are many AI coding assistants (Copilot, Cursor, Tabnine, …). They are powerful but often expensive, tied to specific models, and in some cases not as good at reasoning as other LLMs available on the web.

Snib keeps you flexible:
- Use any LLM - free, paid, reasoning-strong, or lightweight.  
- Use your favorite model’s web UI while Snib prepares your code for input.
- Get AI assistance without handing over control of your entire project.
- Keep full ownership of your project. The AI assists, but you remain the developer.

## 🚀 Features

- Recursively scan entire projects.  
- Flexibly include or exclude files/folders using globs and prefix patterns.  
- Generate prompt-ready chunks with configurable size.  
- Built-in tasks: `debug`, `comment`, `refactor`, `optimize`, `summarize`, `document`, `test`, `analyze`.  
- Smart mode automatically focuses on source code and ignores irrelevant files.  
- Detailed logging at INFO or DEBUG level.  
- Simple CLI with three commands: `init`, `scan`, and `clean`.  

---

## 📦 Installation 

```bash
pip install https://github.com/patmllr/snib/releases/latest/download/snib-0.4.1-py3-none-any.whl
```

Alternatively download the latest wheel here: [Latest Release](https://github.com/patmllr/snib/releases/latest)

### 🧰 Recommended setup

1. Create a Python virtual environment in your project folder:

```bash
python -m venv venv
```

2. Activate the virtual environment and install Snib as shown above.

## ⚡ CLI Usage

`snib` scans projects and generates prompt-ready chunks.

```bash
snib [OPTIONS] COMMAND [ARGS]...
```

### ⚙️ Global Options

| Option                     | Description                              |
| -------------------------- | ---------------------------------------- |
| `--verbose / --no-verbose` | Show INFO logs (default: `--no-verbose`) |
| `--install-completion`     | Install shell completion                 |
| `--show-completion`        | Show completion script                   |
| `--help`                   | Show this message and exit               |

### 📦 Commands

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
| `--output-dir PATH`     | `-o`  | Output folder (default: `promptready`)                                                                  |
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

## 👍 Rule of Thumb for Chunk Size

Since Snib chunks by characters, the following guidelines can help to estimate the chunk size:

| Model / LLM           | Max Context (Tokens) | Recommended `--chunk-size` (Chars) | Notes                                      |
| --------------------- | -------------------- | ---------------------------------- | ------------------------------------------ |
| LLaMA 2 (7B/13B)      | 4,000                | 12,000 – 14,000                    | 1 token ≈ 3–4 chars                        |
| Mistral 7B            | 8,000                | 28,000                             | Leave a safety margin                      |
| GPT-4 classic         | 8,000                | 28,000                             |                                            |
| GPT-4-32k             | 32,000               | 110,000                            |                                            |
| GPT-4o / GPT-5 (128k) | 128,000              | 450,000 – 500,000                  | Very large models, massive chunks possible |

## 🔧 Presets

Presets are predefined `.toml` configuration files that simplify using Snib across different project types (Python, Web, C++, Unity, etc.). They’re optional - without a preset, Snib falls back to the default configuration.

### 📂 Location

```bash
src/snib/presets/
```

### 🏗️ Structure

Each preset follows the same structure as the default `snibconfig.toml`:

```text
[config]
description = "Preset description"
author = "author"
version = "1.0"

[project]
path = "."
description = ""

[instruction]
task = ""

[filters]
include = []
exclude = []
smart_include = []
smart_exclude = []
default_exclude = []
no_default_exclude = false
smart = false

[output]
chunk_size = 30000
force = false

[instruction.task_dict]
debug = "Debug: ..."
comment = "Comment: ..."
refactor = "Refactor: ..."
optimize = "Optimize: ..."
summarize = "Summarize: ..."
document = "Document: ..."
test = "Test: ..."
analyze = "Analyze: ..."
```

### 🚀 Available Presets

Included: `cpp`, `datascience`, `java`, `python`, `unity`, `unreal`, `web` (.toml)  

💡 These serve as starting points and can be adjusted or extended by the community.

### 🛠️ Creating Your Own Preset

1. Copy an existing preset (e.g., `python.toml`).
2. Adjust the `[filters]` section (include, exclude) to match your project.
3. Update the `[config]` section.
4. Test your preset locally on your project with:

```bash
snib init --preset-custom "custom.toml"
snib scan
```

### 🤝 Contribute Presets

Community contributions of new presets or improvements are welcome! 

How to submit a preset:

1. Fork the repository.
2. Add your preset file in src/snib/presets/ (e.g., rust.toml, go.toml, terraform.toml).
3. Make sure your preset:
    - 📖 Contains a clear `[config]` section.
    - ✔️ Has meaningful include / exclude rules.
    - 🧪 Has been tested locally.
    - 🔍 Uses a descriptive filename (e.g., `rust.toml`, not `preset1.toml`).
4. Open a Pull Request with a short explanation of:
    - The project type the preset is for.
    - Any specifics about the filters.

💡 Presets are the easiest way to contribute - even if you don’t know Python.

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
Exclude patterns: ['prompts', 'dist', 'junk', 'venv', '__pycache__']
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

After running `snib scan`, prompt files are written to the `prompts` folder and are ready to get copied to the clipboard:

```text
prompt_1.txt
...
prompt_4.txt
```

## 🧠 Best Practices

- Use a virtual environment inside your project directory.
- Run with `--smart` to focus on source code and skip large irrelevant files.  
- Adjust `--chunk-size` for your target LLM (see [Chunk Size Table](#-rule-of-thumb-for-chunk-size)).  

## 🌱 Contributing New Features

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add new feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

## 📝 Notes

- Snib is designed to be lightweight and easily integrated into CI/CD pipelines.
- Automatically inserts headers in multi-chunk outputs to guide LLM processing.
- Works cross-platform (Windows, Linux, macOS).
- Not battle tested yet.

## 🔮 Future Outlook

Snib is **model-agnostic**, **lightweight**, and keeps **you in control** - unlike expensive, locked AI assistants.

Why Snib remains useful:  
- 🌍 Works with any LLM, including new open-source models.  
- 🧩 CLI-based, fits into any project, CI/CD pipeline, or workflow.  
- 🤝 Community presets extend support across languages and frameworks.  
- 🛠️ AI assists without replacing you - developers stay in charge.  

## 📜 License

MIT License © 2025 Patrick Müller
