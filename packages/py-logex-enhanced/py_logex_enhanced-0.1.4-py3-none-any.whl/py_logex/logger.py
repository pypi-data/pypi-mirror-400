"""Logger implementation for py_logex."""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger as _loguru_logger

from .config import get_config_manager
from .exceptions import format_exception_for_logging
from .utils import ensure_directory_exists

_handler_ids = []


def _configure_logger():
    """Configure the global loguru logger once (idempotent, multi-process safe)."""
    global _handler_ids

    if _handler_ids:
        return

    try:
        _loguru_logger.remove()
    except ValueError:
        pass

    config_manager = get_config_manager()
    config = config_manager.get_logger_config()
    log_file = config.get("file", "app.log")
    log_path = Path(log_file)

    if not log_path.is_absolute():
        log_path = Path.cwd() / log_path

    log_path = log_path.resolve()

    ensure_directory_exists(log_path)

    handler_id = _loguru_logger.add(
        sink=str(log_path),
        format=config.get("format"),
        level=config.get("level"),
        rotation=config.get("rotation"),
        retention=config.get("retention"),
        compression=config.get("compression"),
        mode="a",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )
    _handler_ids.append(handler_id)

    console_config = config.get("console", {})
    if console_config.get("enabled", True):
        console_id = _loguru_logger.add(
            sink=lambda msg: print(msg, end=""),
            format=config.get("format", "{message}"),
            level=console_config.get("level", config.get("level", "INFO")),
            colorize=console_config.get("colorize", True),
        )
        _handler_ids.append(console_id)


class PyLogexLogger:
    """Wrapper around loguru logger."""

    _LEVEL_MAP = {
        "DEBUG": "debug",
        "INFO": "info",
        "WARNING": "warning",
        "CRITICAL": "critical",
    }

    def __init__(self, config_path: Optional[Path] = None):
        self._logger = _loguru_logger
        _configure_logger()

        if config_path:
            get_config_manager().load_config(config_path)

    def trace(self, message: str, *args, **kwargs) -> None:
        self._logger.trace(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs) -> None:
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        self._logger.info(message, *args, **kwargs)

    def success(self, message: str, *args, **kwargs) -> None:
        self._logger.success(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        self._logger.critical(message, *args, **kwargs)

    def exception(
        self,
        exc: Exception,
        level: str = "ERROR",
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        formatted = format_exception_for_logging(exc, level, context)
        level_upper = level.upper()

        if level_upper in self._LEVEL_MAP:
            log_method = getattr(self._logger, self._LEVEL_MAP[level_upper])
            log_method(formatted)
        else:
            self._logger.error(formatted)

    def log(self, level: str, message: str, *args, **kwargs) -> None:
        self._logger.log(level, message, *args, **kwargs)

    def bind(self, **kwargs):
        return self._logger.bind(**kwargs)

    def opt(self, **kwargs):
        return self._logger.opt(**kwargs)

    def catch(self, *args, **kwargs):
        return self._logger.catch(*args, **kwargs)

    def complete(self) -> None:
        self._logger.complete()
        sys.stderr.flush()
        sys.stdout.flush()

    def set_config(self, config_path: Path) -> None:
        """Reconfigure with new config."""
        global _handler_ids
        for handler_id in _handler_ids:
            try:
                self._logger.remove(handler_id)
            except ValueError:
                pass
        _handler_ids.clear()
        get_config_manager().load_config(config_path)
        _configure_logger()

    def remove(self, handler_id=None) -> None:
        self._logger.remove(handler_id)

    def add(self, *args, **kwargs):
        return self._logger.add(*args, **kwargs)

    def level(self, *args, **kwargs):
        return self._logger.level(*args, **kwargs)

    def disable(self, name: str) -> None:
        self._logger.disable(name)

    def enable(self, name: str) -> None:
        self._logger.enable(name)

    def configure(self, **kwargs) -> None:
        self._logger.configure(**kwargs)


_default_logger: Optional[PyLogexLogger] = None


def get_logger(config_path: Optional[Path] = None) -> PyLogexLogger:
    """Get logger instance (singleton pattern)."""
    global _default_logger

    if _default_logger is None:
        _default_logger = PyLogexLogger(config_path=config_path)
    elif config_path is not None:
        _default_logger.set_config(config_path)

    return _default_logger
