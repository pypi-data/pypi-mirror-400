# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional
from datatailr import User
from datatailr.wrapper import dt__Tag


def get_log_level() -> int:
    log_level = os.getenv("DATATAILR_LOG_LEVEL", "INFO").upper()
    if log_level in ["TRACE", "DEBUG"]:
        return logging.DEBUG
    elif log_level == "INFO":
        return logging.INFO
    elif log_level == "WARNING":
        return logging.WARNING
    elif log_level == "ERROR":
        return logging.ERROR
    elif log_level == "CRITICAL":
        return logging.CRITICAL
    else:
        return logging.INFO


def ansi_symbols_supported() -> bool:
    """Check if the terminal supports ANSI symbols."""
    if sys.platform.startswith("win"):
        return (
            os.getenv("ANSICON") is not None
            or os.getenv("WT_SESSION") is not None
            or "TERM" in os.environ
            and os.environ["TERM"] == "xterm-256color"
        )
    else:
        return sys.stdout.isatty()


ANSI_AVAILABLE = ansi_symbols_supported()


def color_text(text: str, color_name: str) -> str:
    """Wrap text with ANSI color codes if supported."""
    if not ANSI_AVAILABLE:
        return text

    colors = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }
    color_code = colors.get(color_name.lower(), "")
    reset_code = colors["reset"] if color_code else ""
    return f"{color_code}{text}{reset_code}"


def RED(text: str) -> str:
    return color_text(text, "red")


def GREEN(text: str) -> str:
    return color_text(text, "green")


def YELLOW(text: str) -> str:
    return color_text(text, "yellow")


def BLUE(text: str) -> str:
    return color_text(text, "blue")


def MAGENTA(text: str) -> str:
    return color_text(text, "magenta")


def CYAN(text: str) -> str:
    return color_text(text, "cyan")


def BOLD(text: str) -> str:
    return color_text(text, "bold")


class MaxLevelFilter(logging.Filter):
    """Allow only log records at or below a given level."""

    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.level


class MinLevelFilter(logging.Filter):
    """Allow only log records at or above a given level."""

    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= self.level


class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[34m",  # Blue
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[41m",  # Red background
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        timestamp = f"{self.BOLD}{self.formatTime(record)}{self.RESET}"
        level = f"{color}{record.levelname}{self.RESET}"
        message = f"{color}{record.getMessage()}{self.RESET}"
        LOG_FORMAT = f"{timestamp} - {level} - {node_name}:{node_ip} - {user} - {job_name} - {record.name} - [Line {record.lineno}]: {message}"
        return LOG_FORMAT


tag = dt__Tag()
node_name = tag.get("node_name") or "local"
node_ip = tag.get("node_ip")
job_name = os.getenv("DATATAILR_JOB_NAME", "unknown_job")

try:
    user = User.signed_user().name
except Exception:
    import getpass

    user = getpass.getuser()


class DatatailrLogger:
    def __init__(
        self,
        name: str,
        log_file: Optional[str] = None,
        log_level: int = get_log_level(),
    ):
        """
        Initialize the DatatailrLogger.

        :param name: Name of the logger.
        :param log_file: Optional file to log messages to.
        :param log_level: Logging level (default: logging.INFO).
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        formatter = ColoredFormatter()

        # stdout handler (DEBUG/INFO only)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.addFilter(MaxLevelFilter(logging.INFO))
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(stdout_handler)

        # stderr handler (WARNING and above)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.WARNING)
        stderr_handler.addFilter(MinLevelFilter(logging.WARNING))
        stderr_handler.setFormatter(formatter)
        self.logger.addHandler(stderr_handler)

        # Optional file handler
        if log_file:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=10 * 1024 * 1024, backupCount=5
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.enable_opentelemetry()

    def get_logger(self):
        """
        Get the configured logger instance.

        :return: Configured logger.
        """
        return self.logger

    def enable_opentelemetry(self):
        """
        Enable OpenTelemetry integration if available.
        """
        try:
            from opentelemetry.instrumentation.logging import LoggingInstrumentor  # type: ignore

            LoggingInstrumentor().instrument(set_logging_format=True)
        except ImportError:
            pass  # OpenTelemetry is not installed, skip instrumentation
