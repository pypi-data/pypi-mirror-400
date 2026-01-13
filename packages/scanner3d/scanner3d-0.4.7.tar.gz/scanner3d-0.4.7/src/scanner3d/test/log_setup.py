# log_setup.py
import logging
import sys
from pathlib import Path

try:
    import colorama
    colorama.just_fix_windows_console()
except Exception:
    pass


class ColorFormatter(logging.Formatter):
    """ANSI-colored logging formatter."""
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[41m",
    }
    RESET = "\033[0m"

    def format(self, record):
        level = record.levelname
        color = self.COLORS.get(level, self.RESET)
        record.levelname = f"{color}{level}{self.RESET}"
        return super().format(record)


class LoggerSetup:
    @staticmethod
    def configure(
        level: int = logging.DEBUG,
        log_file: str | Path | None = None,
        suppress_matplotlib: bool = True,
    ) -> logging.Logger:
        """
        BASIC MODE:
        - Reconfigures ROOT logger with a console handler and optional file handler.
        - ALL loggers in the system propagate to root → everything is captured.
        """

        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

        handlers: list[logging.Handler] = []

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(ColorFormatter(fmt))
        handlers.append(ch)

        # Per-camera file handler
        if log_file is not None:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(logging.Formatter(fmt))
            handlers.append(fh)

        # 🔥 IMPORTANT: configure ROOT logger — the magic
        logging.basicConfig(
            level=level,
            handlers=handlers,
            force=True,   # clears old handlers → new file per camera
        )

        if suppress_matplotlib:
            logging.getLogger("matplotlib").setLevel(logging.WARNING)

        return logging.getLogger()   # ← return ROOT
