"""Module is to hold start enums."""

from enum import Enum

from ndastro_engine.enums.planet_enum import Planets


class Natchaththirams(Enum):
    """Enum to hold stars."""

    ASWINNI = 1
    BHARANI = 2
    KAARTHIKAI = 3
    ROGHINI = 4
    MIRUGASIRISAM = 5
    THIRUVAATHIRAI = 6
    PUNARPOOSAM = 7
    POOSAM = 8
    AAYILYAM = 9
    MAGAM = 10
    POORAM = 11
    UTHTHIRAM = 12
    ASTHTHAM = 13
    CHITHTHIRAI = 14
    SUVAATHI = 15
    VISAAGAM = 16
    ANUSHAM = 17
    KETTAI = 18
    MOOLAM = 19
    POORAADAM = 20
    UTHTHIRAADAM = 21
    THIRUVONAM = 22
    AVITTAM = 23
    SHATHAYAM = 24
    POORATTAATHI = 25
    UTHTHIRATTAATHI = 26
    REVATHI = 27

    def __str__(self) -> str:
        """Return the display name of the star.

        Returns:
            str: The display name of the star.

        """
        return self.name

    @property
    def owner(self) -> Planets:
        """Return the owner (planet) of the star.

        Returns:
            str: The name of the planet that owns the star.

        """
        owners = {
            1: "kethu",
            2: "venus",
            3: "sun",
            4: "moon",
            5: "mars barycenter",
            6: "rahu",
            7: "jupiter barycenter",
            8: "saturn barycenter",
            9: "mercury",
            10: "kethu",
            11: "venus",
            12: "sun",
            13: "moon",
            14: "mars barycenter",
            15: "rahu",
            16: "jupiter barycenter",
            17: "saturn barycenter",
            18: "mercury",
            19: "kethu",
            20: "venus",
            21: "sun",
            22: "moon",
            23: "mars barycenter",
            24: "rahu",
            25: "jupiter barycenter",
            26: "saturn barycenter",
            27: "mercury",
        }

        return Planets.from_code(owners[self.value])

    @staticmethod
    def to_string(num: int) -> str:
        """Convert star number to display name of the star.

        Args:
            num (int): the star number

        Returns:
            str: return the star name

        """
        return Natchaththirams(num).name

    @staticmethod
    def to_list() -> list[str]:
        """Convert enum to list of enum item name.

        Returns:
            list[str]: list of enum item name

        """
        return [el.name for el in Natchaththirams]
