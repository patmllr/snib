# 🔧 Presets

Presets are predefined `.toml` configuration files that simplify using Snib across different project types (Python, Web, C++, Unity, etc.). They’re optional - without a preset, Snib falls back to the default configuration.

## 📂 Location

```bash
src/snib/presets/
```

## 🏗️ Structure

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

## 🚀 Available Presets

Included: `cpp`, `datascience`, `java`, `python`, `unity`, `unreal`, `web` (.toml)  

💡 These serve as starting points and can be adjusted or extended by the community.

## 🛠️ Creating Your Own Preset

1. Copy an existing preset (e.g., `python.toml`).
2. Adjust the `[filters]` section (include, exclude) to match your project.
3. Update the `[config]` section.
4. Test your preset locally on your project with:

```bash
snib init --preset-custom "custom.toml"
snib scan
```

## 🤝 Contribute Presets

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