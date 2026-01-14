"""Module is to hold enums."""

from enum import IntEnum

from ndastro_engine.enums.planet_enum import Planets


class Houses(IntEnum):
    """Enum to hold houses."""

    HOUSE1 = 1
    HOUSE2 = 2
    HOUSE3 = 3
    HOUSE4 = 4
    HOUSE5 = 5
    HOUSE6 = 6
    HOUSE7 = 7
    HOUSE8 = 8
    HOUSE9 = 9
    HOUSE10 = 10
    HOUSE11 = 11
    HOUSE12 = 12

    def __str__(self) -> str:
        """Return name of the house.

        Returns:
            str: name of the house

        """
        return self.name

    @property
    def owner(self) -> Planets:
        """Get the owner of a given house.

        Returns:
            Planets: The owner of the house.

        """
        house_to_planet = {
            1: Planets.MARS,
            2: Planets.VENUS,
            3: Planets.MERCURY,
            4: Planets.MOON,
            5: Planets.SUN,
            6: Planets.MERCURY,
            7: Planets.VENUS,
            8: Planets.MARS,
            9: Planets.JUPITER,
            10: Planets.SATURN,
            11: Planets.SATURN,
            12: Planets.JUPITER,
        }
        return house_to_planet[self.value]
