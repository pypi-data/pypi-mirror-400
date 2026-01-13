"""Rich logging configuration for consistent output formatting."""

import logging
from rich.logging import RichHandler
from rich.console import Console

# Create console with wider width on stderr (matching FastMCP's approach)
console = Console(stderr=True, width=200, soft_wrap=False)

# Create Rich handler for consistent formatting across all loggers
rich_handler = RichHandler(
    console=console,
    show_time=True,
    show_level=True,
    show_path=False,
    rich_tracebacks=True,
    tracebacks_show_locals=False,
    markup=True,
)


def configure_logging():
    """
    Configure logging with Rich handler for consistent formatting.

    This sets up:
    - Root logger with Rich handler
    - Third-party loggers (uvicorn, fastmcp) with Rich handler
    - Reduced noise from verbose libraries
    """
    # Configure root logger with Rich handler
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[rich_handler],
        force=True  # Override any existing configuration
    )

    # Configure third-party loggers to use the same Rich handler
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastmcp"]:
        lib_logger = logging.getLogger(logger_name)
        lib_logger.handlers.clear()  # Remove existing handlers
        lib_logger.addHandler(rich_handler)
        lib_logger.propagate = False
        lib_logger.setLevel(logging.INFO)

    # Reduce noise from verbose third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_rich_handler() -> RichHandler:
    """
    Get the configured Rich handler for additional logger configuration.

    Returns:
        The shared RichHandler instance used by all loggers
    """
    return rich_handler
