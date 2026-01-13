"""
Core functionality for pyPASreporter.
"""

from pathlib import Path
from typing import Any


def load_evd(source_dir: str | Path) -> dict[str, Any]:
    """Load and parse EVD export files.

    Args:
        source_dir: Path to directory containing EVD export files.

    Returns:
        Dictionary with parsed EVD data.
    """
    try:
        from pypasreporter_evdparser import parse_evd

        return parse_evd(source_dir)
    except ImportError as e:
        raise ImportError(
            "pyPASreporter-EVDparser is not installed. "
            "Install it with: pip install pyPASreporter-EVDparser"
        ) from e


def load_pacli(source_dir: str | Path) -> dict[str, Any]:
    """Load and parse PACLI configuration files.

    Args:
        source_dir: Path to directory containing PACLI export files.

    Returns:
        Dictionary with parsed PACLI configuration data.
    """
    try:
        from pypasreporter_pacliparser import parse_pacli

        return parse_pacli(source_dir)
    except ImportError as e:
        raise ImportError(
            "pyPASreporter-PACLIparser is not installed. "
            "Install it with: pip install pyPASreporter-PACLIparser"
        ) from e
