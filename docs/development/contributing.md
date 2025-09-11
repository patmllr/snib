# Contributing

## Presets

Community contributions of new presets or improvements are welcome! 

!!! info "Submitting a preset"
    1. Fork the repository.
    2. Add your preset file in src/snib/presets/ (e.g., rust.toml, go.toml, terraform.toml).
    3. Make sure your preset:
        - Uses a descriptive filename (e.g., `rust.toml`, not `preset1.toml`).
        - Contains a clear `[config]` section.
        - Has meaningful include / exclude rules.
        - Has been tested locally.
    4. Open a Pull Request against the `staging` branch with a short explanation of:
        - The project type the preset is for.
        - Any specifics about the filters.

!!! question "Why contribute presets?"
    Presets are the easiest way to contribute - even if you don’t know Python!

## Bugs

We appreciate help identifying and fixing bugs! You can contribute by reporting issues or submitting bugfixes.

!!! info "Reporting a bug"
    1. Check the [Issues Tracker](https://github.com/patmllr/snib/issues) to see if the bug has already been reported.
    2. Open a new issue with a clear description, including:
        - Steps to reproduce the bug
        - Expected vs actual behavior
        - Any relevant logs or error messages
    3. Label the issue appropriately (e.g., bug).

!!! info "Fixing a bug"
    1. Fork the repository
    2. Create a branch for your bugfix: `git checkout -b fix/short-description`
    3. Implement and commit your changes: `git commit -m "fix(component): brief description of fix"`
    4. Push your branch to your fork: `git push origin fix/short-description`
    5. Open a Pull Request against the `staging` branch.

## Features

To contribute a new feature, please follow these steps:

!!! info "Adding a feature"
    1. Fork this repository  
    2. Create a dedicated branch: `git checkout -b feature/your-feature`  
    3. Implement and commit your changes: `git commit -m "feat(your-feature): add new feature ..."`  
    4. Push your branch to your fork: `git push origin feature/your-feature`  
    5. Open a Pull Request against the `staging` branch

!!! question "Why use the stagin branch?"
    Pull Requests are tested on the `staging` branch first. Once everything works, changes will be merged into `main`.

## Commit Message Convention

We follow the [Conventional Commits](https://github.com/conventional-commits/conventionalcommits.org) format:

```text
<type>(<scope>): <short description>

[optional longer body]
```

### Types

| Type         | Purpose                                                     | Example                                   |
| ------------ | ----------------------------------------------------------- | ----------------------------------------- |
| **feat**     | A new feature                                               | `feat(cli): add command`                  |
| **fix**      | A bug fix                                                   | `fix(_match_patterns): globs`             |
| **docs**     | Documentation only                                          | `docs(readme): update links`              |
| **style**    | Code style (formatting, whitespace, etc.), no logic changes | `style(balck): apply black`               |
| **refactor** | Code change that neither fixes a bug nor adds a feature     | `refactor(pipeline): simplify`            |
| **test**     | Adding or updating tests                                    | `test(scanner): add tests`                |
| **chore**    | Maintenance, CI/CD, build, dependencies                     | `chore(ci): add new workflow`             |

### Guidelines

!!! info "Make your commits easier to understand"
    - Write commit messages in the imperative mood (e.g., “add feature” instead of “added” or “adds”).
    - Keep the first line under 72 characters.
    - The scope <scope> is optional but recommended.
    - Use the body to explain why the change was made, not just what was done.
    - Aim for clarity and consistency.

