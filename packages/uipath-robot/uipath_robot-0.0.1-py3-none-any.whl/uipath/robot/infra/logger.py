"""CLI Logger for UiPath Robot."""

from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Log levels with visual indicators."""

    INFO = ("●", "\033[36m")  # Cyan dot
    SUCCESS = ("✓", "\033[32m")  # Green checkmark
    WARNING = ("⚠", "\033[33m")  # Yellow warning
    ERROR = ("✗", "\033[31m")  # Red X
    DEBUG = ("·", "\033[90m")  # Gray dot
    SYSTEM = ("→", "\033[35m")  # Magenta arrow


class CLILogger:
    """Clean CLI logger with structured output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    def __init__(self, verbose: bool = False):
        """Initialize logger.

        Args:
            verbose: If True, show debug messages
        """
        self.verbose: bool = verbose
        self._last_section: str | None = None

    def _format_time(self) -> str:
        """Get formatted timestamp."""
        return datetime.now().strftime("%H:%M:%S")

    def _log(self, level: LogLevel, message: str, indent: int = 0):
        """Internal log method.

        Args:
            level: The log level
            message: The message to log
            indent: Indentation level (0-2)
        """
        if level == LogLevel.DEBUG and not self.verbose:
            return

        symbol, color = level.value
        indent_str = "  " * indent
        time_str = f"{self.DIM}{self._format_time()}{self.RESET}"

        print(f"{time_str} {color}{symbol}{self.RESET} {indent_str}{message}")

    def section(self, title: str):
        """Print a section header.

        Args:
            title: Section title
        """
        if self._last_section:
            print()  # Add spacing between sections
        print(f"\n{self.BOLD}{title}{self.RESET}")
        print("─" * len(title))
        self._last_section = title

    def info(self, message: str, indent: int = 0):
        """Log info message."""
        self._log(LogLevel.INFO, message, indent)

    def success(self, message: str, indent: int = 0):
        """Log success message."""
        self._log(LogLevel.SUCCESS, message, indent)

    def warning(self, message: str, indent: int = 0):
        """Log warning message."""
        self._log(LogLevel.WARNING, message, indent)

    def error(self, message: str, indent: int = 0):
        """Log error message."""
        self._log(LogLevel.ERROR, message, indent)

    def debug(self, message: str, indent: int = 0):
        """Log debug message (only if verbose)."""
        self._log(LogLevel.DEBUG, message, indent)

    def system(self, message: str, indent: int = 0):
        """Log system/internal message."""
        self._log(LogLevel.SYSTEM, message, indent)

    def job_start(self, job_key: str, package: str, version: str):
        """Log job start with formatted output."""
        self.section(f"Job {job_key[:8]}...")
        self.info(f"Package: {self.BOLD}{package}{self.RESET} v{version}")

    def heartbeat(self, count: int | None = None):
        """Log heartbeat in a minimal way."""
        if self.verbose:
            msg = f"Heartbeat {count}" if count else "Heartbeat"
            self.debug(msg)

    def package_status(self, package: str, version: str, status: str):
        """Log package download/extraction status.

        Args:
            package: Package ID
            version: Package version
            status: Status message (downloading/extracting/cached)
        """
        if status == "cached":
            self.debug(f"Using cached {package}:{version}")
        elif status == "downloading":
            self.info(f"Downloading {package}:{version}")
        elif status == "extracting":
            self.info("Extracting package", indent=1)
        elif status == "extracted":
            self.success("Package ready", indent=1)

    def environment_setup(self, status: str):
        """Log environment setup status.

        Args:
            status: Status (creating/syncing/ready/skipped)
        """
        if status == "creating":
            self.info("Creating virtual environment", indent=1)
        elif status == "syncing":
            self.info("Installing dependencies", indent=1)
        elif status == "ready":
            self.success("Environment ready", indent=1)
        elif status == "skipped":
            self.debug("No pyproject.toml, skipping venv", indent=1)

    def process_execution(self, status: str, detail: str | None = None):
        """Log process execution status.

        Args:
            status: Status (starting/running/success/failed)
            detail: Optional detail message
        """
        if status == "starting":
            self.info("Starting process execution")
        elif status == "running":
            self.system("Process running", indent=1)
        elif status == "success":
            self.success("Process completed successfully")
            if detail:
                self.debug(f"Output: {detail}", indent=1)
        elif status == "failed":
            self.error("Process execution failed")
            if detail:
                self.error(detail, indent=1)


# Global logger instance
_logger: CLILogger | None = None


def get_logger(verbose: bool = False) -> CLILogger:
    """Get or create the global logger instance.

    Args:
        verbose: Enable verbose logging

    Returns:
        The CLI logger instance
    """
    global _logger
    if _logger is None:
        _logger = CLILogger(verbose=verbose)
    return _logger


def init_logger(verbose: bool = False):
    """Initialize the global logger.

    Args:
        verbose: Enable verbose logging
    """
    global _logger
    _logger = CLILogger(verbose=verbose)
