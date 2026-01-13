"""Enhanced exception handling for py_logex."""

import traceback
from pathlib import Path
from typing import List, Optional


class ExceptionFormatter:
    """Formats exceptions with enhanced file/line information."""

    @staticmethod
    def format_exception(
        exc: Exception, include_locals: bool = True, max_frames: Optional[int] = None
    ) -> str:
        """Format exception with detailed traceback information."""
        exc_type = type(exc).__name__
        exc_msg = str(exc)

        tb = exc.__traceback__
        if tb is None:
            return f"{exc_type}: {exc_msg}"

        frames = traceback.extract_tb(tb)
        if max_frames:
            frames = frames[-max_frames:]

        lines = [f"\n{exc_type}: {exc_msg}"]
        lines.append("\nTraceback (most recent call last):")

        for frame in frames:
            file_path = Path(frame.filename)
            lines.append(f'  File "{file_path}", line {frame.lineno}, in {frame.name}')
            if frame.line:
                lines.append(f"    {frame.line.strip()}")
        lines.append(f"\n{exc_type}: {exc_msg}")

        return "\n".join(lines)

    @staticmethod
    def _extract_frames(exc: Exception) -> List:
        """Extract frames from exception traceback."""
        tb = exc.__traceback__
        if tb is None:
            return []
        return traceback.extract_tb(tb)

    @staticmethod
    def get_exception_context(exc: Exception) -> dict:
        """Extract context information from exception."""
        frames = ExceptionFormatter._extract_frames(exc)

        if not frames:
            return {
                "type": type(exc).__name__,
                "message": str(exc),
                "file": None,
                "line": None,
                "function": None,
            }

        last_frame = frames[-1]
        return {
            "type": type(exc).__name__,
            "message": str(exc),
            "file": str(Path(last_frame.filename).name),
            "full_path": last_frame.filename,
            "line": last_frame.lineno,
            "function": last_frame.name,
            "code": last_frame.line.strip() if last_frame.line else None,
        }


_formatter = ExceptionFormatter()
_LEVEL_METHOD_MAP = {
    "DEBUG": "debug",
    "INFO": "info",
    "WARNING": "warning",
    "CRITICAL": "critical",
}


def format_exception_for_logging(
    exc: Exception, level: str = "ERROR", context: Optional[dict] = None
) -> str:
    """Format exception specifically for logging output."""
    exc_context = _formatter.get_exception_context(exc)

    parts = []

    parts.append(f"{exc_context['type']}: {exc_context['message']}")

    if exc_context["file"]:
        location = f"{exc_context['file']}"
        if exc_context["function"]:
            location += f":{exc_context['function']}"
        if exc_context["line"]:
            location += f":{exc_context['line']}"
        parts.append(f"Location: {location}")

    if exc_context["code"]:
        parts.append(f"Code: {exc_context['code']}")

    parts.append("\n" + _formatter.format_exception(exc))

    if context:
        parts.append(f"\nContext: {context}")

    return "\n".join(parts)
