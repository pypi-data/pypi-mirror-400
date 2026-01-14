"""Configuration management module for ndastro_engine.

This module provides the ConfigurationManager class for handling
application configuration settings in a centralized manner.
"""

import struct
from pathlib import Path

from skyfield.iokit import Loader

from ndastro_engine.utils import get_app_data_dir


class ConfigurationManager:
    """Manages application configuration settings.

    This class provides a centralized way to handle configuration settings for the application.
    It initializes with default settings and can be extended to load, validate, and manage
    various configuration parameters.

    Attributes:
        settings (dict): A dictionary containing configuration key-value pairs.

    """

    def __init__(self) -> None:
        """Initialize the ConfigurationManager with default settings."""
        try:
            data_dir = get_app_data_dir("ndastro")
            Path(data_dir).mkdir(parents=True, exist_ok=True)

            # Custom loader for downloading and caching .bsp files
            loader = Loader(data_dir, verbose=True)

            self.ts = loader.timescale()

            # Try to load ephemeris, delete and retry if corrupted
            ephemeris_file = "de440t.bsp"
            try:
                self.eph = loader(ephemeris_file)
            except (struct.error, ValueError):
                # File is corrupted, delete and retry
                corrupted_file = Path(data_dir) / ephemeris_file
                if corrupted_file.exists():
                    print(f"Detected corrupted ephemeris file, deleting: {corrupted_file}")
                    corrupted_file.unlink()
                    print("Re-downloading ephemeris file...")
                    self.eph = loader(ephemeris_file)
                else:
                    raise
        except Exception as e:
            msg = f"Failed to initialize astronomical data. Check your internet connection or disk space to download the ephemeris file. Error: {e}"
            raise RuntimeError(msg) from e


# Instantiate the object here
_ndastro_config = ConfigurationManager()
ts = _ndastro_config.ts
eph = _ndastro_config.eph
