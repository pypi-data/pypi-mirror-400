"""Constants for ndastro engine.

This module defines constant values used throughout the ndastro_engine package.
"""

OS_WIN = "win32"
OS_MAC = "darwin"
OS_LINUX = "linux"

DEGREE_MAX = 360.0

# Lahiri Ayanamsa constants (referenced to J2000.0)
AYANAMSA_AT_J2000 = 22.460148  # Ayanamsa value at J2000.0 epoch
DEG_PER_JCENTURY = 1.396042  # Linear term (degrees per Julian century)
DEG_PER_SQUARE_JCENTURY = 0.000308  # Quadratic term (degrees per square Julian century)

CENTURY_19 = 1900
CENTURY_20 = 2000
CENTURY_21 = 2100
