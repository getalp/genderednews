"""
An enum listing possible article categories.
"""
import enum
import gn_modules.misc as gn_misc


class Category(gn_misc.AutoName):
    """List the uniform category names."""
    INTERNATIONAL = enum.auto()
    FRANCE = enum.auto()
    SOCIETE = enum.auto()
    ECONOMIE = enum.auto()
    POLITIQUE = enum.auto()
    DEBATS_ET_OPINIONS = enum.auto()
    EDUCATION = enum.auto()
    RELIGION = enum.auto()
    CULTURE = enum.auto()
    SPORT = enum.auto()
    SANTE = enum.auto()
    NUMERIQUE = enum.auto()
    ENTREPRISES = enum.auto()
    PEOPLE = enum.auto()
    FAIT_DIVERS = enum.auto()
    SCIENCE_ET_ENVIRONNEMENT = enum.auto()
    INDEFINI = enum.auto()

    def to_string(self) -> str:
        """From Category to string."""
        return self.value

    @staticmethod
    def from_string(key) -> 'Category':
        """From string to Category."""
        return Category(key)
