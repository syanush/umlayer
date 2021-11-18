from enum import Enum


class Abilities(Enum):
    EDITABLE_TEXT = 1


class BaseElement(object):
    def getAbilities(self):
        return self._abilities
