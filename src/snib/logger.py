import inspect
import logging

import typer

# TODO: NOTICE (NOTE) (Custom Level between info and warning) = „userinfos“ (e.g. „Output folder created …“)
# TODO: not only --verbose (DEBUG vs INFO), also: --quiet (WARN + ERROR), --trace (more than DEBUG, all filenames on read...)

# colors for levels
LEVEL_COLORS = {
    logging.DEBUG: typer.colors.BLUE,
    logging.INFO: typer.colors.GREEN,
    logging.WARNING: typer.colors.YELLOW,
    logging.ERROR: typer.colors.RED,
    25: typer.colors.MAGENTA,  # CONFIRM
    26: typer.colors.CYAN,
}

CONFIRM_LEVEL = 25
NOTICE_LEVEL = 26

logging.addLevelName(logging.DEBUG, "DBUG")
logging.addLevelName(logging.INFO, "INFO")
logging.addLevelName(logging.WARNING, "WARN")
logging.addLevelName(logging.ERROR, "ERRO")
logging.addLevelName(CONFIRM_LEVEL, "CONF")
logging.addLevelName(NOTICE_LEVEL, "NOTE")


class SnibLogger(logging.Logger):
    """
    Custom Logger for Snib with CONFIRM and NOTICE levels.

    This logger extends the standard Python logging.Logger and adds:
    - `notice()`: logs a NOTICE-level message (custom level 26).
    - `confirm()`: prompts the user with a yes/no question, logging it at CONFIRM level (custom level 25).

    The logger supports standard levels: DEBUG, INFO, WARNING, ERROR, plus the custom levels.
    """

    def notice(self, msg: str, *args, **kwargs):
        """
        Logs a message at NOTICE level (custom level 26).

        Args:
            msg (str): The message to log.
            *args: Additional positional arguments for the logger.
            **kwargs: Additional keyword arguments for the logger.
        """
        if self.isEnabledFor(NOTICE_LEVEL):
            self._log(NOTICE_LEVEL, msg, args, **kwargs)

    def confirm(self, msg: str, default: bool = False) -> bool:
        """
        Prompts the user with a yes/no confirmation and returns the response.

        Logs the prompt at CONFIRM level (custom level 25) and prints a
        formatted prefix. Loops until the user enters a valid response.

        Args:
            msg (str): The message/question to display to the user.
            default (bool): The default value if the user presses Enter
                without typing 'y' or 'n'. Defaults to False.

        Returns:
            bool: True if user confirms, False otherwise.
        """
        if self.isEnabledFor(CONFIRM_LEVEL):
            # build prefix for log-record
            if self.handlers:
                frame = inspect.currentframe().f_back
                record = logging.LogRecord(
                    name=self.name,
                    level=CONFIRM_LEVEL,
                    pathname=frame.f_code.co_filename,
                    lineno=frame.f_lineno,
                    msg=msg,
                    args=(),
                    exc_info=None,
                )
                prefix = self.handlers[0].formatter.format(record)
            else:
                prefix = f"[CONFIRM] {self.name}: {msg}"

            # prompt
            prompt_text = f"{prefix} [y/N]: "
            while True:
                response = input(prompt_text).strip().lower()
                if response == "":
                    return default
                if response in ("y", "yes"):
                    return True
                if response in ("n", "no"):
                    return False
                self.info("Please enter Y or N.")


class ColoredFormatter(logging.Formatter):
    """
    Formatter that applies colors to log output based on level.

    Uses Typer colors to style:
        - DEBUG: Blue
        - INFO: Green
        - WARNING: Yellow
        - ERROR: Red
        - CONFIRM: Magenta
        - NOTICE: Cyan

    Also dims the logger name in bright black.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record with colored levelname and logger name.

        Args:
            record (logging.LogRecord): The record to format.

        Returns:
            str: The formatted and colored log string.
        """
        record.levelname = typer.style(
            record.levelname, fg=LEVEL_COLORS.get(record.levelno, typer.colors.WHITE)
        )
        record.name = typer.style(record.name, fg=typer.colors.BRIGHT_BLACK)
        return super().format(record)


# global logger, but level set later
logging.setLoggerClass(SnibLogger)
logger = logging.getLogger("snib")
ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.NOTSET)  # level set later via set_verbose()!


def set_verbose(verbose: bool):
    """
    Set the logging verbosity for the global logger.

    Adjusts levels for all handlers and applies a colored format.

    Args:
        verbose (bool): If True, sets level to DEBUG, else INFO.

    Notes:
        - Verbose mode also includes timestamp and module info.
        - Normal mode shows only level and message.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)
    for h in logger.handlers:
        h.setLevel(level)
        fmt = (
            "[%(levelname)s] [%(asctime)s] %(name)s.%(module)s: %(message)s"
            if verbose
            else "[%(levelname)s] %(message)s"
        )
        h.setFormatter(ColoredFormatter(fmt, datefmt="%H:%M:%S"))
