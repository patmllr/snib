# Pipeline

The snib pipeline organizes the process from scanning a project directory to producing ready-to-use prompt files.  

## Steps

1. **Scanner**  
   Collects files and metadata from the project.  
   👉 [See Scanner for details](scanner.md)

2. **Formatter**  
   Converts collected `Sections` into formatted prompt-ready text.  
   👉 [See Formatter for details](formatter.md)

3. **Chunker**  
   Splits prompt text into manageable chunks.  
   👉 [See Chunker for details](chunker.md)

4. **Writer**  
   Saves chunks as text files in the output directory.  
   👉 [See Writer for details](writer.md)

---

## Workflow Overview

```mermaid
flowchart TD
    A[Scanner] -->|Sections| B[Formatter]
    B -->|Prompt Text| C[Chunker]
    C -->|Chunks| D[Writer]
    D -->|prompt_*.txt| E[(Output Folder)]
