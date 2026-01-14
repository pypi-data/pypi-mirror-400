"""Core astronomical calculation functions for the ndastro engine.

This module provides functions for calculating:
- Planet positions (tropical and sidereal)
- Ascendant position
- Lunar node positions (Rahu and Kethu)
- Sunrise and sunset times
"""

from datetime import datetime, timedelta
from math import atan2, degrees, radians, tan
from typing import TYPE_CHECKING, cast

from skyfield.almanac import cos, find_discrete, sin, sunrise_sunset
from skyfield.data.spice import inertial_frames
from skyfield.elementslib import osculating_elements_of
from skyfield.framelib import ecliptic_frame
from skyfield.nutationlib import mean_obliquity
from skyfield.toposlib import wgs84

from ndastro_engine.config import eph, ts
from ndastro_engine.enums.planet_enum import Planets
from ndastro_engine.utils import normalize_degree

if TYPE_CHECKING:
    from skyfield.positionlib import Barycentric
    from skyfield.timelib import Time
    from skyfield.units import Angle
    from skyfield.vectorlib import VectorSum


def get_planet_position(planet: Planets, lat: float, lon: float, given_time: datetime, ayanamsa: float | None = None) -> tuple[float, float, float]:
    """Return the tropical position of the planet for the given latitude, longitude, and datetime.

    Args:
        planet (Planets): The planet to calculate the position for.
        lat (float): The latitude of the observer in decimal degrees.
        lon (float): The longitude of the observer in decimal degrees.
        given_time (datetime): The datetime of the observation in UTC.
        ayanamsa (float | None): The ayanamsa value to adjust the longitude for sidereal calculations.

    Returns:
        tuple[float, float, float]: The tropical latitude, longitude, and distance of the planet.

    """
    t = ts.utc(given_time)

    if planet in (Planets.RAHU, Planets.KETHU):
        pos = get_lunar_node_positions(given_time)
        return (
            0.0,
            pos[0] if planet == Planets.RAHU else pos[1],
            0.0,
        )

    if planet == Planets.ASCENDANT:
        asc_lon = get_ascendent_position(lat, lon, given_time, ayanamsa)
        return (0.0, asc_lon, 0.0)

    if planet == Planets.EMPTY:
        return (0.0, 0.0, 0.0)

    observer: VectorSum = eph["earth"] + wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon, elevation_m=914)
    astrometric = cast("Barycentric", observer.at(t)).observe(eph[planet.code]).apparent()

    latitude, longitude, distance = astrometric.frame_latlon(ecliptic_frame)

    return cast(
        "tuple[float, float, float]",
        (latitude.degrees, longitude.degrees if ayanamsa is None else (cast("float", longitude.degrees) - ayanamsa), distance.au),
    )


def get_all_planet_positions(
    lat: float, lon: float, given_time: datetime, ayanamsa: float | None = None
) -> dict[Planets, tuple[float, float, float]]:
    """Return the tropical positions of all planets for the given latitude, longitude, and datetime.

    Args:
        lat (float): The latitude of the observer in decimal degrees.
        lon (float): The longitude of the observer in decimal degrees.
        given_time (datetime): The datetime of the observation in UTC.
        ayanamsa (float | None): The ayanamsa value to adjust the longitude for sidereal calculations.

    Returns:
        dict[Planets, tuple[float, float, float]]: A dictionary mapping each planet to its tropical/sidereal latitude,
            longitude, and distance. If ayanamsa is provided, then the longitude values are adjusted for sidereal
            calculations.

    """
    positions: dict[Planets, tuple[float, float, float]] = {}
    for planet in Planets:
        positions[planet] = get_planet_position(planet, lat, lon, given_time, ayanamsa)

    return positions


def get_sunrise_sunset(lat: float, lon: float, given_time: datetime, elevation: float = 914) -> tuple[datetime, datetime]:
    """Calculate the sunrise and sunset times for a given location and date.

    Args:
        lat (float): The latitude of the location in decimal degrees.
        lon (float): The longitude of the location in decimal degrees.
        given_time (datetime): The date and time for which to calculate the sunrise and sunset times.
        elevation (float, optional): The elevation of the location in meters. Defaults to 914 meters (approximately 3000 feet).

    Returns:
        tuple[datetime, datetime]: A tuple containing the sunrise and sunset times as datetime objects.

    """
    # Define location
    location = wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon, elevation_m=elevation)

    # Define time range for the search (e.g., one day)
    t_start = ts.utc(given_time.date())  # Start of the day
    t_end = ts.utc(given_time.date() + timedelta(days=1))  # End of the day

    # Find sunrise time
    f = sunrise_sunset(eph, location)
    times, events = find_discrete(t_start, t_end, f)

    sunrise, sunset = cast("list[Time]", [time for time, _ in zip(times, events, strict=False)])

    return cast("tuple[datetime, datetime]", (sunrise.utc_datetime(), sunset.utc_datetime()))


def get_ascendent_position(lat: float, lon: float, given_time: datetime, ayanamsa: float | None = None) -> float:
    """Calculate the tropical/sidereal ascendant.

    Args:
        lat (float): The latitude of the observer in decimal degrees.
        lon (float): The longitude of the observer in decimal degrees.
        given_time (datetime): The datetime of the observation.
        ayanamsa (float | None): The ayanamsa value to adjust the longitude for sidereal calculations.

    Returns:
        float: The longitude of the tropical/sidereal ascendant.

    """
    t = ts.utc(given_time)

    oe = mean_obliquity(t.tdb) / 3600
    oer = radians(oe)

    gmst: float = cast("float", t.gmst)

    lst = (gmst + lon / 15) % 24

    lstr = radians(lst * 15)

    # source: https://astronomy.stackexchange.com/a/55891 by pm-2ring
    ascr = atan2(cos(lstr), -(sin(lstr) * cos(oer) + tan(radians(lat)) * sin(oer)))

    asc = degrees(ascr)

    return normalize_degree(asc if ayanamsa is None else asc - ayanamsa)


def get_lunar_node_positions(given_time: datetime) -> tuple[float, float]:
    """Calculate the positions of the lunar nodes (Rahu and Kethu) for a given datetime.

    Args:
        given_time (datetime): The datetime in UTC for which to calculate the lunar node positions.

    Returns:
        tuple[float, float]: A tuple containing the longitudes of Rahu and Kethu in decimal degrees.

    """
    tm = ts.utc(given_time)
    ecliptic = inertial_frames["ECLIPJ2000"]

    earth = eph["earth"]
    moon = eph["moon"]
    position = cast("VectorSum", (moon - earth)).at(tm)
    elements = osculating_elements_of(position, ecliptic)

    rahu_position = cast("float", cast("Angle", elements.longitude_of_ascending_node).degrees)
    kethu_position = normalize_degree(rahu_position + 180)

    return rahu_position, kethu_position
