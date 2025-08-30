import logging

from .cli import parse_args, main

if __name__ == "__main__":
    args = parse_args()

    if getattr(args, "dev", False):
        log_level = logging.DEBUG
    elif getattr(args, "verbose", False):
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    main()