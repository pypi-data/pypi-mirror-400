# colorstreak/logger.py
from __future__ import annotations

import os
from typing import ClassVar


class Logger:
    """
    Minimal color logger, print-compatible.

    Styles:
      - "full":   prefix + message in the same color (default)
      - "prefix": only prefix colored, message normal
      - "soft":   prefix colored, message same color but dimmed
    """

    RESET: ClassVar[str] = "\033[0m"
    BOLD: ClassVar[str] = "\033[1m"
    DIM: ClassVar[str] = "\033[2m"

    COLORS: ClassVar[dict[str, str]] = {
        "debug": "\033[92m",    # GREEN
        "info": "\033[94m",     # BLUE
        "warning": "\033[93m",  # YELLOW
        "error": "\033[91m",    # RED
        "library": "\033[95m",  # MAGENTA
        "success": "\033[92m",  # GREEN

        # --- extra helpers (still minimal) ---
        "step": "\033[96m",     # CYAN
        "note": "\033[90m",     # GRAY
        "metric": "\033[95m",   # MAGENTA
        "title": "\033[94m",    # BLUE (but bold)
    }

    STYLE: ClassVar[str] = os.getenv("COLORSTREAK_STYLE", "full").lower()
    ENABLED: ClassVar[bool] = os.getenv("NO_COLOR", "") == ""

    @classmethod
    def configure(cls, *, style: str | None = None, enabled: bool | None = None) -> None:
        """
        Configure global logger behavior.
        - style: "full" | "prefix" | "soft"
        - enabled: True/False (if False, prints without ANSI colors)
        """
        if style is not None:
            s = style.lower().strip()
            if s not in {"full", "prefix", "soft"}:
                raise ValueError("style must be: 'full', 'prefix', or 'soft'")
            cls.STYLE = s
        if enabled is not None:
            cls.ENABLED = bool(enabled)

    @staticmethod
    def _join_print_args(values: tuple[object, ...], sep: str) -> str:
        return sep.join("" if v is None else str(v) for v in values)

    @classmethod
    def _print(cls, level: str, *values: object, **kwargs) -> None:
        """
        Print-compatible wrapper:
        accepts sep=, end=, file=, flush= like print().
        """
        sep = kwargs.pop("sep", " ")
        end = kwargs.pop("end", "\n")
        file = kwargs.pop("file", None)
        flush = kwargs.pop("flush", False)

        prefix = f"[{level.upper()}]"
        message = cls._join_print_args(values, sep=sep)

        if not cls.ENABLED:
            print(f"{prefix} {message}", end=end, file=file, flush=flush)
            return

        color = cls.COLORS.get(level, cls.RESET)

        if level == "title":
            # Title is intentionally bold blue regardless of style
            out = f"{color}{cls.BOLD}{prefix} {message}{cls.RESET}"
            print(out, end=end, file=file, flush=flush)
            return

        if cls.STYLE == "prefix":
            out = f"{color}{prefix}{cls.RESET} {message}"
        elif cls.STYLE == "soft":
            out = f"{color}{cls.BOLD}{prefix}{cls.RESET} {color}{cls.DIM}{message}{cls.RESET}"
        else:  # "full"
            out = f"{color}{prefix} {message}{cls.RESET}"

        print(out, end=end, file=file, flush=flush)

    # ====== Base levels ======

    @staticmethod
    def debug(*values: object, **kwargs) -> None:
        """GREEN: debug-level logs."""
        Logger._print("debug", *values, **kwargs)

    @staticmethod
    def info(*values: object, **kwargs) -> None:
        """BLUE: informational logs."""
        Logger._print("info", *values, **kwargs)

    @staticmethod
    def warning(*values: object, **kwargs) -> None:
        """YELLOW: warning logs."""
        Logger._print("warning", *values, **kwargs)

    @staticmethod
    def error(*values: object, **kwargs) -> None:
        """RED: error logs."""
        Logger._print("error", *values, **kwargs)

    @staticmethod
    def library(*values: object, **kwargs) -> None:
        """MAGENTA: library/internal logs."""
        Logger._print("library", *values, **kwargs)

    @staticmethod
    def success(*values: object, **kwargs) -> None:
        """GREEN: success logs (semantic alias)."""
        Logger._print("success", *values, **kwargs)

    # ====== Helpers (requested) ======

    @staticmethod
    def step(*values: object, **kwargs) -> None:
        """CYAN: step/progress logs (useful for workflows)."""
        Logger._print("step", *values, **kwargs)

    @staticmethod
    def note(*values: object, **kwargs) -> None:
        """GRAY: low-priority notes (quiet, non-intrusive)."""
        Logger._print("note", *values, **kwargs)

    @staticmethod
    def title(*values: object, **kwargs) -> None:
        """BOLD BLUE: section titles (high visibility)."""
        Logger._print("title", *values, **kwargs)

    @staticmethod
    def metric(*values: object, **kwargs) -> None:
        """MAGENTA: metrics/log lines (loss/acc/latency/etc)."""
        Logger._print("metric", *values, **kwargs)