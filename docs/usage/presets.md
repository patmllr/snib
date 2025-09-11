# Presets

Presets are predefined `.toml` configuration files that simplify using snib across different project types (Python, Web, C++, Unity, etc.). They’re optional - without a preset, snib falls back to the default configuration.

!!! question "Why use presets"
    Presets save you time and provide a solid starting point. They also help maintain consistency across projects.

## Structure

Each preset follows the same structure as the default `snibconfig.toml`:

??? note "Show Default Config"
    <small>

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
    </small>

## Available Presets

Included: `cpp`, `datascience`, `java`, `python`, `unity`, `unreal`, `web` (.toml)  

!!! question "Why is there only so little"
    These serve as starting points and can be adjusted or extended by the community.

## Creating Your Own Preset

!!! tip "Quick Start"
    1. Copy an existing preset (e.g., `python.toml`).
    2. Adjust the `[filters]` section (include, exclude) to match your project.
    3. Update the `[config]` section.
    4. Test your preset locally.

```bash
snib init --preset-custom "custom.toml"
snib scan
```

If you’d like to support the community, feel free to contribute your own presets. See [Contributing](../development/contributing.md).