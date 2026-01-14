"""Ayanamsa calculation functions for Vedic astrology.

This module provides functions to calculate various ayanamsa (precession correction)
values used in Vedic astrology, including:
- Lahiri, Raman, Krishnamurti, Fagan-Bradley ayanamsas
- Traditional systems: Kali, Janma, Yukteshwar, Suryasiddhanta, Aryabhatta
- Star-based systems: True Citra, True Revati, True Pusya
- Other systems: Madhava, Vishnu, Ushashasi, and True ayanamsa

Each function calculates the ayanamsa for a given date using a quadratic formula
based on Julian centuries from the J2000.0 epoch.
"""

import datetime

from ndastro_engine.constants import J2000_JD, JULIAN_CENTURY_DAYS
from ndastro_engine.core import ts


def get_lahiri_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Lahiri Ayanamsa for a given date."""
    # Constants in the Lahiri Ayanamsa formula
    # At J2000 (2000-01-01), Lahiri ayanamsa = 23:51:00 = 23.85°
    # At 2100-01-01, Lahiri ayanamsa = 25:15:00 = 25.25° (astro-seek.com)
    c0 = 23.8500190824  # Constant term adjusted for J2000 epoch
    c1 = 1.3999090000  # Linear term (degrees per Julian century)
    c2 = 0.000091  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_raman_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Raman Ayanamsa for a given date."""
    # Constants in the Raman Ayanamsa formula
    # At J2000 (2000-01-01 12:00), Raman ayanamsa = 22:24:44 = 22.412222°
    # At 2100-01-01, Raman ayanamsa = 23:48:00 = 23.8° (astro-seek.com)
    c0 = 22.4122411064  # Constant term adjusted for J2000 epoch (accounts for B6 ≈ -0.0000136689)
    c1 = 1.3874488936  # Linear term (degrees per Julian century)
    c2 = 0.00031  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_kali_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Kali Ayanamsa for a given date."""
    # Constants in the Kali Ayanamsa formula
    c0 = 27.4  # Constant term
    c1 = 1.138  # Linear term (degrees per Julian century)
    c2 = 0.00031  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_krishnamurti_new_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Krishnamurti Ayanamsa for a given date."""
    # Constants in the Krishnamurti Ayanamsa formula
    # At J2000 (2000-01-01), KP ayanamsa = 23:45:00 = 23.75°
    # At 2100-01-01, KP ayanamsa = 25:09:00 = 25.15° (astro-seek.com)
    c0 = 23.7500212483  # Constant term adjusted for J2000 epoch
    c1 = 1.3998270000  # Linear term (degrees per Julian century)
    c2 = 0.000173  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_krishnamurti_old_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Krishnamurti Old Ayanamsa for a given date."""
    # Constants in the Krishnamurti Old Ayanamsa formula
    # KP Old is 15 seconds (0.0041666667°) less than KP New
    # At J2000 (2000-01-01), KP Old ayanamsa = 23:44:45 = 23.745833°
    # At 2100-01-01, KP Old ayanamsa = 25:08:45 = 25.145833° (astro-seek.com)
    c0 = 23.7458545816  # Constant term adjusted for J2000 epoch
    c1 = 1.3998270000  # Linear term (degrees per Julian century, same as KP New)
    c2 = 0.000173  # Quadratic term (degrees per square Julian century, same as KP New)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_fagan_bradley_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Fagan-Bradley Ayanamsa for a given date."""
    # Constants in the Fagan-Bradley Ayanamsa formula
    # At J2000 (2000-01-01 12:00), Fagan-Bradley ayanamsa = 24:44:00 = 24.733333°
    # At 2100-01-01, Fagan-Bradley ayanamsa = 26:08:00 = 26.133333° (astro-seek.com)
    c0 = 24.7333524228  # Constant term adjusted for J2000 epoch
    c1 = 1.3998053333  # Linear term (degrees per Julian century)
    c2 = 0.000195  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_janma_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Janma Ayanamsa for a given date."""
    # Constants in the Janma Ayanamsa formula
    c0 = 22.4602  # Constant term
    c1 = 1.7193  # Linear term (degrees per Julian century)
    c2 = 0.00025  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_true_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the True Ayanamsa for a given date."""
    # Constants in the True Ayanamsa formula
    c0 = 24.0422  # Constant term
    c1 = 1.3978  # Linear term (degrees per Julian century)
    c2 = 0.00031  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_madhava_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Madhava Ayanamsa for a given date."""
    # Constants in the Madhava Ayanamsa formula
    c0 = 23.8958  # Constant term
    c1 = 1.5545  # Linear term (degrees per Julian century)
    c2 = 0.00022  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_vishnu_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Vishnu Ayanamsa for a given date."""
    # Constants in the Vishnu Ayanamsa formula
    c0 = 24.0084  # Constant term
    c1 = 1.3978  # Linear term (degrees per Julian century)
    c2 = 0.00031  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_yukteshwar_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Yukteshwar Ayanamsa for a given date."""
    # Constants in the Yukteshwar Ayanamsa formula
    # At J2000 (2000-01-01), Yukteshwar ayanamsa = 22:28:00 = 22.466667°
    # At 2100-01-01, Yukteshwar ayanamsa = 23:52:00 = 23.866667° (astro-seek.com)
    c0 = 22.4666901676  # Constant term adjusted for J2000 epoch
    c1 = 1.3996356667  # Linear term (degrees per Julian century)
    c2 = 0.000364  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_suryasiddhanta_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Suryasiddhanta Ayanamsa for a given date."""
    # Constants in the Suryasiddhanta Ayanamsa formula
    c0 = 24.0  # Constant term
    c1 = 1.39656  # Linear term (degrees per Julian century)
    c2 = 0.00022  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_aryabhatta_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Aryabhatta Ayanamsa for a given date."""
    # Constants in the Aryabhatta Ayanamsa formula
    c0 = 23.7  # Constant term
    c1 = 1.5  # Linear term (degrees per Julian century)
    c2 = 0.0002  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_ushashasi_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the Ushashasi Ayanamsa for a given date."""
    # Constants in the Ushashasi Ayanamsa formula
    # At J2000 (2000-01-01), Ushashasi ayanamsa = 20:03:00 = 20.05°
    # At 2100-01-01, Ushashasi ayanamsa = 21:27:00 = 21.45° (astro-seek.com)
    c0 = 20.0500191365  # Constant term adjusted for J2000 epoch
    c1 = 1.3998300000  # Linear term (degrees per Julian century)
    c2 = 0.000170  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_true_citra_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the True Citra Ayanamsa for a given date."""
    # Constants in the True Citra Ayanamsa formula
    # At J2000 (2000-01-01), True Citra ayanamsa = 23:50:00 = 23.833333°
    # At 2100-01-01, True Citra ayanamsa = 25:14:00 = 25.233333° (astro-seek.com)
    c0 = 23.8333523331  # Constant term adjusted for J2000 epoch
    c1 = 1.3999903333  # Linear term (degrees per Julian century)
    c2 = 0.00001  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_true_revati_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the True Revati Ayanamsa for a given date."""
    # Constants in the True Revati Ayanamsa formula
    # At J2000 (2000-01-01), True Revati ayanamsa = 20:02:00 = 20.033333°
    # At 2100-01-01, True Revati ayanamsa = 21:26:00 = 21.433333° (astro-seek.com)
    c0 = 20.0333527432  # Constant term adjusted for J2000 epoch
    c1 = 1.3998343333  # Linear term (degrees per Julian century)
    c2 = 0.000166  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def get_true_pusya_ayanamsa(date: datetime.datetime) -> float:
    """Calculate the True Pusya Ayanamsa for a given date."""
    # Constants in the True Pusya Ayanamsa formula
    c0 = 24.1  # Constant term
    c1 = 1.38  # Linear term (degrees per Julian century)
    c2 = 0.00026  # Quadratic term (degrees per square Julian century)

    # Calculate b6
    b6 = _calculate_b6((date.year, date.month, date.day))

    return c0 + c1 * b6 + c2 * (b6**2)


def _calculate_b6(date: tuple[int, int, int]) -> float:
    """Calculate B6 parameter (Julian centuries from J2000.0).

    B6 represents the time in Julian centuries from the J2000.0 epoch.
    At J2000.0 (2000-01-01 12:00 TT), B6 = 0.0

    Args:
        date: Tuple of (year, month, day)

    Returns:
        Number of Julian centuries from J2000.0 epoch

    """
    # Calculate Julian Date using Skyfield
    t = ts.utc(*date)
    jd = t.tt  # Julian Date in Terrestrial Time

    # Compute B6 parameter: centuries from J2000.0 epoch
    return (jd - J2000_JD) / JULIAN_CENTURY_DAYS
