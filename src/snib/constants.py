SMART_CODE_EXTENSIONS = [
    "*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c", "*.cs", "*.go", "*.rb", "*.php",
    "*.html", "*.css", "*.scss", "*.less", "*.json", "*.yaml", "*.yml", "*.xml", "*.sh",
    "*.bat", "*.ps1", "*.pl", "*.swift", "*.kt", "*.m", "*.r", "*.sql"
]

SMART_IGNORE_EXTENSIONS = [
    "*.log", "*.zip", "*.tar", "*.gz", "*.bin", "*.exe", "*.dll", "*.csv"
]

DEFAULT_EXCLUDE = ["venv", "promptready", "__pycache__, .git"]

TASK_INSTRUCTIONS = {
    "debug": "Debug: Analyze the code and highlight potential errors, bugs, or inconsistencies.",
    "comment": "Comment: Add comments or explain existing functions and code sections.",
    "refactor": "Refactor: Suggest refactorings to make the code cleaner, more readable, and maintainable.",
    "optimize": "Optimize: Improve efficiency or performance of the code.",
    "summarize": "Summarize: Provide a concise summary of the files or modules.",
    "document": "Document: Generate documentation for functions, classes, or modules.",
    "test": "Test: Create unit tests or test cases for the code.",
    "analyze": "Analyze: Perform static analysis or security checks on the code."
}