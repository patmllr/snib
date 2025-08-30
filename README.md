# Snib ✂️

**Snib** is a CLI Python tool to scan projects, collect source files, and generate **prompt-ready chunks** for use with large language models (LLMs). It supports filtering by file types, folders, regex and can optionally run in **smart mode** to automatically ignore large logs or binary files.

## 🚀 Features 

- Scan entire projects recursively.
- Include or exclude files/folders with globs or explicit paths.
- Generate prompt-ready chunks with configurable size.
- Built-in tasks: `debug`, `comment`, `refactor`, `optimize`, `summarize`, `document`, `test`, `analyze`.
- Smart mode automatically focuses on source code and ignores unnecessary files.
- Detects conflicts between include/exclude patterns.
- Logs scanning and processing details at INFO or DEBUG level.
- Clean and organized prompt output for large projects.

---

## 📦 Installation 

```bash
pip install https://github.com/patmllr/snib/releases/latest/download/snib-0.2.1-py3-none-any.whl
```

Alternatively download the latest wheel here: [Latest Release](https://github.com/patmllr/snib/releases/latest)

### 🧰 Recommended setup

Create a Python virtual environment inside your project folder and install `snib` in the `venv`:

```bash
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
source venv/bin/activate       # Linux / macOS
pip install https://github.com/patmllr/snib/releases/latest/download/snib-0.2.1-py3-none-any.whl
```

## ⚡ Usage

```bash
snib --path ./my_project \
     --description "This is a demo." \
     --include "*.py, test.js, src/test" \
     --exclude "*.log, *.tmp" \
     --chunk-size 10000 \
     --output promptready \
     --task debug \
     --smart \
     --verbose
```

### ⚙️ Options

| Option                  | Short | Description                                                                                             |
| ----------------------- | ----- | ------------------------------------------------------------------------------------------------------- |
| `--path`                | `-p`  | Path to scan (default: current directory)                                                               |
| `--description`         | `-d`  | Short description of the project/changes                                                                |
| `--include`             | `-i`  | File types or folders to include, e.g., `*.py, cli.py`                                                  |
| `--exclude`             | `-e`  | File types or folders to exclude, e.g., `*.pyc, __pycache__`                                            |
| `--chunk-size`          | `-c`  | Max characters per chunk (default: 30,000)                                                              |
| `--output`              | `-o`  | Folder to save prompt-ready chunks (default: `promptready`)                                             |
| `--force`               | `-f`  | Force overwrite existing prompt files                                                                   |
| `--task`                | `-t`  | Predefined task: `debug`, `comment`, `refactor`, `optimize`, `summarize`, `document`, `test`, `analyze` |
| `--verbose`             | `-V`  | Show INFO logs                                                                                          |
| `--dev`                 | `-D`  | Show DEBUG logs                                                                                         |
| `--smart`               | `-s`  | Smart mode: includes only code files, ignores large/log files                                           |
| `--no-default-excludes` | `-E`  | Disable automatic exclusion of `venv`, `promptready`, `__pycache__`                                     |

## 👍 Rule of Thumb for Chunk Sizes

Since snib chunks by characters, the following guidelines can help to estimate the chunk size:

| Model / LLM           | Max Context (Tokens) | Recommended `--chunk-size` (Chars) | Notes                                      |
| --------------------- | -------------------- | ---------------------------------- | ------------------------------------------ |
| LLaMA 2 (7B/13B)      | 4,000                | 12,000 – 14,000                    | 1 token ≈ 3–4 chars                        |
| Mistral 7B            | 8,000                | 28,000                             | Leave a safety margin                      |
| GPT-4 classic         | 8,000                | 28,000                             |                                            |
| GPT-4-32k             | 32,000               | 110,000                            |                                            |
| GPT-4o / GPT-5 (128k) | 128,000              | 450,000 – 500,000                  | Very large models, massive chunks possible |

## 🗂️ Example Project Scan

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
│       ├── chunker.py
│       ├── cli.py
│       ├── constants.py
│       ├── formatter.py
│       ├── models.py
│       ├── scanner.py
│       ├── utils.py
│       └── writer.py
└── tests
    ├── test_chunker.py
    ├── test_cli_scan.py
    ├── test_formatter.py
    ├── test_scanner.py
    ├── test_utils.py
    └── test_writer.py

#[FILE] tests\test_chunker.py
import pytest
from snib.chunker import Chunker

...

#[INFO]
Prompt file 4/4

        for file_path in self.output_dir.glob("prompt_*.txt"):
            if file_path.is_file():
                file_path.unlink()
        logger.info(f"Cleared existing prompt file(s) in {self.output_dir}")


#[FILE] src\snib\__init__.py


#[FILE] src\snib\__main__.py
from .cli import main

if __name__ == "__main__":
    main()
```

After running snib, a `promptready` folder is generated with prompt files ready to get copied to the clipboard:

```text
prompt_1.txt
...
promt_4.txt
```

## 🧠 Best Practices

- Always install snib inside a virtual environment.
- `venv` and `promptready` are automatically excluded from scans.
- Use `--smart` to focus on code and avoid unnecessary large files.
- Adjust `--chunk-size` based on your target LLM and the table above.
- If followed these instructions just exclude some folders you don't need to be scanned and run snib on your project like:

```bash
snib -e "dist, junk" --chunk-size 100000 --smart --verbose
```

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