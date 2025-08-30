import argparse
from pathlib import Path
import logging

from .scanner import Scanner
from .utils import handle_include_args, handle_exclude_args, detect_pattern_conflicts, check_include_in_exclude
from .tasks import TASK_INSTRUCTIONS
from .extensions import SMART_CODE_EXTENSIONS, SMART_IGNORE_EXTENSIONS

logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(
        description="snib scans projects and generates prompt-ready chunks",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # path to scan
    parser.add_argument(
        "--path", "-p",
        nargs="?",
        default=".",
        help="Path to scan (default: current directory)"
    )

    # project description
    parser.add_argument(
        "--description", "-d",
        type=str,
        default="",
        help="Short description of the project and changes you want to make (default: empty string)"
    )

    # include filters
    parser.add_argument(
        "--include", "-i",
        type=str,
        default="all",
        help="Datatypes or folders/files to included, e.g. *.py, cli.py (default: all)"
    )

    # exclude filters
    parser.add_argument(
        "--exclude", "-e",
        type=str,
        default="",
        help="Datatypes or folders/files to excluded, e.g *.pyc, __pycache__ (default: none)"
    )

    # chunk size
    parser.add_argument(
        "--chunk-size", "-c",
        type=int,
        default=30000,
        help=("Max number of characters per chunk (default: 30000)\nRule of thumb: 1 token ≈ 3-4 chars.")
    )

    # output directory (TODO: path and name?)
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="promptready",
        help="Folder to save the prompt ready data chunks (default: 'promptready')"
    )

    # force overwrite
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force delete existing prompt files and write new ones without validation"
    )

    # predefined tasks
    parser.add_argument(
    "--task", "-t",
    type=str,
    choices=TASK_INSTRUCTIONS.keys(),
    default="",
    help="Select a predefined task for the model, e.g. debug or test (default: none)"
    )

    # info logs
    parser.add_argument(
    "--verbose", "-V",
    action="store_true",
    help="Show INFO logs (default: WARNING only)"
    )

    # debug logs
    parser.add_argument(
        "--dev", "-D",
        action="store_true",
        help="Show DEBUG logs for development (default: WARNING only)"
    )

    # smart mode
    parser.add_argument(
    "--smart", "-s",
    action="store_true",
    help="Smart mode automatically includes only code files and ignores large data/log files"
    )

    return parser.parse_args()

def main():
    args = parse_args()
    path = Path(args.path).resolve()
    scanner = Scanner(path)

    # user filters
    user_include = handle_include_args(args.include.split(","))
    user_exclude = handle_exclude_args(args.exclude.split(","))

    if args.smart:
        # combine user filters with smart defaults
        include_patterns = list(set(user_include + SMART_CODE_EXTENSIONS))
        exclude_patterns = list(set(user_exclude + SMART_IGNORE_EXTENSIONS))
    else:
        include_patterns = user_include
        exclude_patterns = user_exclude

    conflicts = detect_pattern_conflicts(include_patterns, exclude_patterns)
    if conflicts:
        logger.warning(f"Pattern conflicts detected (Exclude wins): {conflicts}")
        # optional: del in include_patterns
        include_patterns = [p for p in include_patterns if not any(p in c for c in conflicts)]

    problematic_includes = check_include_in_exclude(path, include_patterns, exclude_patterns)
    if problematic_includes:
        logger.warning(f"The following include patterns are inside excluded folders and will be ignored: {problematic_includes}")
        # optional: del in include_patterns
        include_patterns = [p for p in include_patterns if not any(p in c for c in problematic_includes)]
    
    logger.debug(f"Final include patterns: {include_patterns}")
    logger.debug(f"Final exclude patterns: {exclude_patterns}")

    scanner.scan(
        description=args.description,
        include=include_patterns,
        exclude=exclude_patterns,
        chunk_size=args.chunk_size,
        output_dir=args.output,
        force=args.force,
        task=args.task
    )

