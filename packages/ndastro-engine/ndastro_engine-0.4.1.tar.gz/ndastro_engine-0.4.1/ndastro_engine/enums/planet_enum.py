"""Module is to hold planet enums."""

from enum import IntEnum


class Planets(IntEnum):
    """Enum to hold planets."""

    EMPTY = -1
    ASCENDANT = 0
    SUN = 1
    MOON = 2
    MARS = 3
    MERCURY = 4
    JUPITER = 5
    VENUS = 6
    SATURN = 7
    RAHU = 8
    KETHU = 9

    @staticmethod
    def to_string(num: int) -> str:
        """Convert planet number to display name of the planet.

        Args:
            num (int): the planet number

        Returns:
            str: return the planet name

        """
        return Planets(num).name if num in Planets._value2member_map_ else "empty"

    @staticmethod
    def from_code(code: str) -> "Planets":
        """Convert planet code to planet enum.

        Args:
            code (str): the planet code

        Returns:
            Planets: the corresponding planet enum

        """
        planet_codes = {
            "empty": Planets.EMPTY,
            "ascendant": Planets.ASCENDANT,
            "sun": Planets.SUN,
            "moon": Planets.MOON,
            "mars barycenter": Planets.MARS,
            "mercury": Planets.MERCURY,
            "jupiter barycenter": Planets.JUPITER,
            "venus": Planets.VENUS,
            "saturn barycenter": Planets.SATURN,
            "rahu": Planets.RAHU,
            "kethu": Planets.KETHU,
        }

        return planet_codes.get(code, Planets.EMPTY)

    @staticmethod
    def to_list() -> list[str]:
        """Convert planet enum to list of planet name.

        Returns:
            list[str]: list of planet names

        """
        return [el.name for el in Planets]

    @property
    def code(self) -> str:
        """Return the planet code.

        Returns:
            str: the planet code

        """
        planet_codes = {
            Planets.EMPTY: "empty",
            Planets.ASCENDANT: "ascendant",
            Planets.SUN: "sun",
            Planets.MOON: "moon",
            Planets.MARS: "mars barycenter",
            Planets.MERCURY: "mercury",
            Planets.JUPITER: "jupiter barycenter",
            Planets.VENUS: "venus",
            Planets.SATURN: "saturn barycenter",
            Planets.RAHU: "rahu",
            Planets.KETHU: "kethu",
        }

        return planet_codes.get(self, "empty")

    @property
    def color(self) -> str:
        """Return the planet color code.

        Returns:
            str: the planet color code

        """
        planet_colors = {
            Planets.EMPTY: "#000000",  # Black
            Planets.ASCENDANT: "#FFFFFF",  # White
            Planets.SUN: "#FFD700",  # Gold
            Planets.MOON: "#C0C0C0",  # Silver
            Planets.MARS: "#FF0000",  # Red
            Planets.MERCURY: "#008000",  # Green
            Planets.JUPITER: "#FFFF00",  # Yellow
            Planets.VENUS: "#FF69B4",  # Pink
            Planets.SATURN: "#00008B",  # DarkBlue
            Planets.RAHU: "#8A2BE2",  # BlueViolet
            Planets.KETHU: "#8B0000",  # DarkRed
        }

        return planet_colors.get(self, "#000000")  # Default to Black
