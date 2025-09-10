<h1 align="center">
<img src="https://gist.githubusercontent.com/patmllr/4fa5d1b50a1475c91d8323c75de8a2a2/raw/26ea2b9795a70cf65fc753b5b8eb3ac64f300cc7/snib.svg" width="300">
</h1><br>


[![PyPI version](https://img.shields.io/pypi/v/snib.svg)](https://pypi.org/project/snib/)
[![Build](https://github.com/patmllr/snib/actions/workflows/release.yml/badge.svg)](https://github.com/patmllr/snib/actions/workflows/release.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0f5cf59b56334f75a75892804f237677)](https://app.codacy.com/gh/patmllr/snib/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/0f5cf59b56334f75a75892804f237677)](https://app.codacy.com/gh/patmllr/snib/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/patmllr/snib)](https://github.com/patmllr/snib/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/patmllr/snib)](https://github.com/patmllr/snib/pulls)

**Snib** is a Python CLI tool to scan your projects and generate prompt-ready chunks for use with LLMs.

## 💡 Why Snib?

Today there are many AI coding assistants such as Copilot, Cursor, and Tabnine. They are powerful but often expensive, tied to specific models, and in some cases not as good at reasoning as other LLMs available on the web.

Snib keeps you flexible:
- Use any LLM - free, paid, reasoning-strong, or lightweight.  
- Use your favorite model’s web UI while Snib prepares your code for input.
- Get AI assistance without handing over control of your entire project.

## 🚀 Features

- Recursively scan entire projects.  
- Flexibly include or exclude files/folders using globs and prefix patterns.  
- Generate prompt-ready chunks with configurable size.  
- Built-in tasks: `debug`, `comment`, `refactor`, `optimize`, `summarize`, `document`, `test`, `analyze`.  
- Smart mode: focus on source code, ignore irrelevant files.
- Detailed logging at INFO or DEBUG level.  
- Simple CLI with three commands: `init`, `scan`, and `clean`.  

## 📦 Installation 

```bash
pip install snib
```

Alternatively download the latest wheel here: [Latest Release](https://github.com/patmllr/snib/releases/latest)

## ⚡ Quick Start

```text
pip install snib
cd /path/to/your/project
snib init
snib scan --smart
```

## 📚 Documentation

Full documentation is available at [Docs](DOCS-LINK):
- [Usage](USAGE-LINK) - getting started, CLI, and examples
- [Configuration](CONFIGURATION-LINK) - presets, snibconfig.toml
- [Development](DEVELOPMENT-LINK) - code structure, testing, contributing

## 📝 Notes

- Snib is designed to be lightweight and easily integrated into CI/CD pipelines.
- Automatically inserts headers in multi-chunk outputs to guide LLM processing.
- Works cross-platform (Windows, Linux, macOS).
- Not battle tested yet.

## 🤝 Contributing

Want to help improve Snib? Check the [Development](DEVELOPMENT-LINK) docs.

💡 An easy way to contribute is by creating or improving **presets** for different project types. Presets are simple `.toml` files that define include/exclude rules and default tasks, making Snib immediately usable for more developers. Check the [Prerets](PRESETS-LINK) docs.

## 📜 License

MIT License © 2025 Patrick Müller
