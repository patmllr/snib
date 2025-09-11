<h1 align="center">
<img src="https://gist.githubusercontent.com/patmllr/4fa5d1b50a1475c91d8323c75de8a2a2/raw/26ea2b9795a70cf65fc753b5b8eb3ac64f300cc7/snib.svg" width="300">
</h1><br>

[Powered by COFFEE](https://img.shields.io/badge/powered%20by-COFFEE-orange.svg?style=flat&colorA=E1523D&colorB=007D8A)
[![PyPI version](https://img.shields.io/pypi/v/snib.svg)](https://pypi.org/project/snib/)
[![Build](https://github.com/patmllr/snib/actions/workflows/release.yml/badge.svg)](https://github.com/patmllr/snib/actions/workflows/release.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0f5cf59b56334f75a75892804f237677)](https://app.codacy.com/gh/patmllr/snib/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/0f5cf59b56334f75a75892804f237677)](https://app.codacy.com/gh/patmllr/snib/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)
[![Issues](https://img.shields.io/github/issues/patmllr/snib)](https://github.com/patmllr/snib/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/patmllr/snib)](https://github.com/patmllr/snib/pulls)

**Snib** is a Python CLI tool to scan your projects and generate prompt-ready chunks for use with LLMs.

## 💡 Why Snib?

Today there are many AI coding assistants such as Copilot, Cursor, and Tabnine. They are powerful but often expensive, tied to specific models, and in some cases not as good at reasoning as other LLMs available on the web.

Snib keeps you flexible:
- Use any LLM - free, paid, reasoning-strong, or lightweight.  
- Use your favorite model’s web UI while snib prepares your code for input.

## 🚀 Features

- Recursively scan projects with include/exclude rules.
- Generate prompt-ready chunks with configurable sizes.
- Section formatting and built-in tasks to guide the AI.
- Simple CLI with three commands: `init`, `scan`, and `clean`.

## 📦 Installation 

```bash
pip install snib
```

Alternatively download the latest wheel here: [Latest Release](https://github.com/patmllr/snib/releases/latest)

## ⚡ Quick Start

```text
cd /path/to/your/project
snib init
snib scan --smart
```

## 📚 Documentation

Full documentation is available at [https://patmllr.github.io/snib/](https://patmllr.github.io/snib/):
- [Usage](https://patmllr.github.io/snib/usage/getting-started/): Learn how to run snib and configure it.
- [Development](https://patmllr.github.io/snib/development/contributing/): Contributing, testing, and internal structure.
- [API Reference](https://patmllr.github.io/snib/reference/pipeline/): Automatically generated from the code docstrings.

## 🤝 Contribute

Help improve snib by contributing presets, features, or bug fixes. See [Contributing](https://patmllr.github.io/snib/development/contributing/).

## 📜 License

MIT License © 2025 Patrick Müller
