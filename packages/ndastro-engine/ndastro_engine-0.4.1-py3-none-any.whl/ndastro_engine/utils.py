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


def dms2dd(degrees: int, minutes: int, seconds: float, sign: int = 1) -> float:
    """Convert degrees, minutes, and seconds to decimal degrees.

    Args:
        degrees (int): The degrees component.
        minutes (int): The minutes component.
        seconds (float): The seconds component.
        sign (int, optional): The sign of the angle. Defaults to 1 (positive).

    Returns:
        float: The angle in decimal degrees.

    """
    decimal_degrees = abs(degrees) + minutes / 60 + seconds / 3600
    return sign * decimal_degrees


def dd2dms(decimal_degrees: float) -> tuple[int, int, float, int]:
    """Convert decimal degrees to degrees, minutes, and seconds.

    Args:
        decimal_degrees (float): The angle in decimal degrees.

    Returns:
        tuple[int, int, float, int]: A tuple containing degrees, minutes, seconds, and sign.

    """
    sign = 1 if decimal_degrees >= 0 else -1
    abs_degrees = abs(decimal_degrees)
    degrees = int(abs_degrees)
    minutes_full = (abs_degrees - degrees) * 60
    minutes = int(minutes_full)
    seconds = (minutes_full - minutes) * 60
    return degrees, minutes, seconds, sign


def dd2dmsstr(decimal_degrees: float) -> str:
    """Convert decimal degrees to a formatted DMS string.

    Args:
        decimal_degrees (float): The angle in decimal degrees.

    Returns:
        str: The angle in DMS format as a string.

    """
    degrees, minutes, seconds, sign = dd2dms(decimal_degrees)
    sign_str = "" if sign >= 0 else "-"
    return f"{sign_str}{degrees}° {minutes}' {seconds:.2f}\""
