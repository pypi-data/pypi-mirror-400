"""
py_logex - Simple, powerful logging with built-in exception handling and YAML configuration.

Usage:
    from py_logex import logger

    logger.info("Application started")

    try:
        risky_operation()
    except Exception as e:
        logger.exception(e)
"""

__version__ = "0.1.4"

from .logger import get_logger

logger = get_logger()

__all__ = [
    "logger",
    "get_logger",
    "__version__",
]
