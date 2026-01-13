"""Utility functions for py_logex."""

import inspect
import sys
from pathlib import Path
from typing import List, Optional


def get_script_name() -> str:
    """Get the name of the script that's running (without .py extension)."""
    try:
        if hasattr(sys.modules["__main__"], "__file__"):
            main_file = sys.modules["__main__"].__file__
            if main_file:
                return Path(main_file).stem
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_file = frame.f_back.f_code.co_filename
            return Path(caller_file).stem
    except Exception:
        pass

    return "app"


def walk_up_find_file(
    filename: str, start_path: Optional[Path] = None, max_levels: int = 5
) -> Optional[Path]:
    """Walk up directory tree looking for a specific file."""
    if start_path is None:
        start_path = Path.cwd()

    current = start_path
    for _ in range(max_levels):
        file_path = current / filename
        if file_path.exists() and file_path.is_file():
            return file_path

        parent = current.parent
        if parent == current:
            break
        current = parent

    return None


def get_common_config_locations(filename: str = "logging.yaml") -> List[Path]:
    """Get list of common configuration file locations to check."""
    cwd = Path.cwd()
    home = Path.home()

    locations = [
        cwd / filename,
        cwd / "config" / filename,
        cwd / "configs" / filename,
        cwd / "src" / "config" / filename,
        cwd / ".config" / filename,
        home / ".py_logex" / filename,
    ]

    return locations


def ensure_directory_exists(file_path: Path) -> None:
    """Ensure the directory for a file path exists."""
    directory = file_path.parent
    directory.mkdir(parents=True, exist_ok=True)
