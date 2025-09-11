# Getting Started

## Installation 

```bash
pip install snib
```

Alternatively download the latest wheel here: [Latest Release](https://github.com/patmllr/snib/releases/latest)

!!! tip "Recommended Setup"

    1. Navigate to your project folder:

        ```text
        cd /path/to/your/project
        ```

    2. Create a Python virtual environment in your project folder:

        ```text
        python -m venv venv
        ```

    3. Activate the virtual environment:

        - Linux/macOS:

          ```text
          source venv/bin/activate
          ```

        - Windows CMD:

          ```text
          venv\Scripts\activate
          ```

    4. Install snib as shown above.

## Running Snib 

After setting up a virtual environment and installing snib, you can run commands directly inside your project folder. Start by initializing your project:

```bash
snib init
```
This generates the default config and output folder:

!!!success "Initialisation succesfull"
    [NOTE] /path/to/your/project/snibconfig.toml generated with defaults

    [NOTE] Output folder created at /path/to/your/project/prompts

Now scan your project. For small to medium projects, `--smart` is usually enough:

```bash
snib scan --smart
```

On medium-sized projects you may see a warning like this:

!!! warning "Too many files included"
    [WARN] Included files exceed 100. This may lead to large prompts and higher costs.

In such cases, review your include/exclude rules.
A good starting point is to check your project directory for files or folders that don’t need to be processed.

For example, if you have a folder called junk that also contains source code, the `--smart` option includes it by default.
You should explicitly exclude it using the `--exclude` option:

```bash
snib scan --smart --exclude "junk"
```

!!! info "Large or complex projects"
    Keep your scans lean by excluding irrelevant files.  
    Use `--exclude` / `--include` patterns or edit `snibconfig.toml`.  
    Presets can also help for common project types (see [Presets](presets.md)).


If you try to include and exclude the same pattern, snib detects a pattern conflict:

```bash
snib scan --smart --exclude "junk" --include "junk"
```

!!! warning "Pattern conflicts"
    [WARN] Pattern conflicts detected (Exclude wins): {'junk'}

Snib resolves such conflicts by always letting the exclude win.
This makes it possible to combine broad includes with specific excludes:

```bash
snib scan --smart --exclude "test.py"
```

!!! warning "Pattern conflicts"
    [WARN] Pattern conflicts detected (Exclude wins): {'*.py (conflicts with test.py)'}

Here `--smart` includes all `*.py` files, but the explicit exclude removes `test.py`.
Thanks to the exclude wins rule, all Python files are included except `test.py`.

You can also guide the AI with a description and a task (see [Tasks](tasks.md)):

```bash
snib scan --smart --description "I want to change ..." --task refactor
```

After scanning, snib creates prompt files (`prompt_1.txt`, …) in the `prompts` folder.

??? note "Show Prompt Example"
    <small>

    ```text
    #[INFO]
    Please do not give output until all prompt files are sent. Prompt file 1/4

    #[DESCRIPTION]
    I want to change ...

    #[TASK]
    Refactor: Suggest refactorings to make the code cleaner, more readable, and maintainable.

    #[INCLUDE/EXCLUDE]
    Include patterns: ['*.py']
    Exclude patterns: ['venv', 'prompts', ..., 'snibconfig.toml']
    Included files: files: 34, total size: 92.79 KB
    Excluded files: files: 20181, total size: 339.37 MB

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

    </small>

For large models you might want to increase the chunk size:

```bash
snib scan --smart --description "..." --task refactor --chunk-size 100000
```

!!! tip "Choosing the right chunk size"
    See the [Chunk Size Table](#chunk-size) below.

To reset everything (e.g. broken config), run:

```bash
snib clean 
```

!!! info "Running outside the project path"
    If you don’t run snib from your project folder, use the `--path` option with every command (`init`, `scan`, `clean`).


## Chunk Size

| Model / LLM           | Max Context (Tokens) | Recommended `--chunk-size` (Chars) | Notes                                      |
| --------------------- | -------------------- | ---------------------------------- | ------------------------------------------ |
| LLaMA 2 (7B/13B)      | 4,000                | 12,000 – 14,000                    | 1 token ≈ 3–4 chars                        |
| Mistral 7B            | 8,000                | 28,000                             | Leave a safety margin                      |
| GPT-4 classic         | 8,000                | 28,000                             |                                            |
| GPT-4-32k             | 32,000               | 110,000                            |                                            |
| GPT-4o / GPT-5 (128k) | 128,000              | 450,000 – 500,000                  | Very large models, massive chunks possible |

!!! info "Rule of Thumb"
    These are rough estimates to guide you when setting `--chunk-size`. Snib chunks by characters, not tokens, so chunk sizes vary by model. Always adjust based on your model's context limit and safety margin.

## Advanced

- `--no-default-excludes`: Don’t exclude venv, prompts, or snibconfig.toml.
- `--force`: Runs commands without confirmation.

!!! warning "Use with caution"
    The `--force` option can overwrite existing files or create unwanted text files if your include/exclude rules are not set correctly.

!!! info "Commands and Options"
    For a list of all commands and options take a look at [CLI Usage](cli.md).