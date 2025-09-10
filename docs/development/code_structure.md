# Code Structure

The Snib pipeline manages the full project workflow: initializing a project, scanning directories to generate prompt-ready files, and cleaning up generated output.

```mermaid
flowchart LR
    %% Erste Reihe: Init
    Init["INIT"] --> Scan["SCAN"]

    %% Zweite Reihe: Scan-Unterprozesse
    Scanner["Scanner"] --> Formatter["Formatter"]
    Formatter --> Chunker["Chunker"]
    Chunker --> Writer["Writer"]
    Writer --> Output["prompt_*.txt"]

    %% Pfeil vom Scan-Knoten zur Unterprozessreihe
    Scan --> Scanner

    %% Dritte Reihe: Clean (optional)
    Output -.-> Clean["CLEAN"]
```

_Content coming soon._