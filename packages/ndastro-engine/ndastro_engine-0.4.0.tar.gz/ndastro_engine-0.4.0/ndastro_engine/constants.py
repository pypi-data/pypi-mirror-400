"""Constants for ndastro engine.

This module defines constant values used throughout the ndastro_engine package.
"""

OS_WIN = "win32"
OS_MAC = "darwin"
OS_LINUX = "linux"

DEGREE_MAX = 360.0

# J2000.0 epoch: January 1, 2000, 12:00 TT (Terrestrial Time)
J2000_JD = 2451545.0  # Julian Date of J2000.0 epoch
JULIAN_CENTURY_DAYS = 36525.0  # Number of days in a Julian century

# Lahiri Ayanamsa constants (referenced to J2000.0)
AYANAMSA_AT_J2000 = 23.856498  # Ayanamsa value at J2000.0 epoch
DEG_PER_JCENTURY = 1.396042  # Linear term (degrees per Julian century)
DEG_PER_SQUARE_JCENTURY = 0.000308  # Quadratic term (degrees per square Julian century)
