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
    """Logger with CONFIRM-Prompt and NOTICE"""

    def notice(self, msg: str, *args, **kwargs):
        if self.isEnabledFor(NOTICE_LEVEL):
            self._log(NOTICE_LEVEL, msg, args, **kwargs)

    def confirm(self, msg: str, default: bool = False) -> bool:
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
    """Formatting with colors"""

    def format(self, record: logging.LogRecord) -> str:
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
logger.setLevel(logging.NOTSET)  # set level later!!!


def set_verbose(verbose: bool):
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
