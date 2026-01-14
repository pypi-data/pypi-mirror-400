"""Utility functions for the ndastro_engine package.

This module provides:
- get_app_data_dir: Get the application data directory for the given app name.
"""

import os
import sys
from pathlib import Path

from ndastro_engine.constants import DEGREE_MAX, OS_MAC, OS_WIN


def get_app_data_dir(appname: str) -> Path:
    """Get the application data directory for the given app name.

    Parameters
    ----------
    appname : str
        Name of the application.

    Returns
    -------
    Path
        Path to the application data directory.

    """
    home = Path.home()
    if sys.platform == OS_WIN:
        return home / "AppData/Local" / appname

    if sys.platform == OS_MAC:
        return home / "Library/Application Support" / appname

    # Linux and other Unix-like systems (uses XDG spec fallback)
    data_home = os.getenv("XDG_DATA_HOME", "~/.local/share")
    return Path(data_home).expanduser() / appname


def normalize_degree(degree: float) -> float:
    """Normalize the degree to be within 0-360.

    Args:
        degree (float): The degree to normalize.

    Returns:
        float: The normalized degree.

    """
    return (degree % DEGREE_MAX + DEGREE_MAX) % DEGREE_MAX
