# Getting Started

## 📦 Installation 

```bash
pip install snib
```

Alternatively download the latest wheel here: [Latest Release](https://github.com/patmllr/snib/releases/latest)

### 🧰 Recommended setup

1. Create a Python virtual environment in your project folder:

```bash
python -m venv venv
```

2. Activate the virtual environment and install Snib as shown above.

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

## 👍 Rule of Thumb for Chunk Size

Since Snib chunks by characters, the following guidelines can help to estimate the chunk size:

| Model / LLM           | Max Context (Tokens) | Recommended `--chunk-size` (Chars) | Notes                                      |
| --------------------- | -------------------- | ---------------------------------- | ------------------------------------------ |
| LLaMA 2 (7B/13B)      | 4,000                | 12,000 – 14,000                    | 1 token ≈ 3–4 chars                        |
| Mistral 7B            | 8,000                | 28,000                             | Leave a safety margin                      |
| GPT-4 classic         | 8,000                | 28,000                             |                                            |
| GPT-4-32k             | 32,000               | 110,000                            |                                            |
| GPT-4o / GPT-5 (128k) | 128,000              | 450,000 – 500,000                  | Very large models, massive chunks possible |

## 🧠 Best Practices

- Use a virtual environment inside your project directory.
- Run with `--smart` to focus on source code and skip large irrelevant files.  
- Adjust `--chunk-size` for your target LLM (see [Chunk Size Table](#-rule-of-thumb-for-chunk-size)).  