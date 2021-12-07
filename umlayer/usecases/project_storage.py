"""Persistent storage for a project
"""

from abc import ABC, abstractmethod

from umlayer import model


class ProjectStorage(ABC):
    """It supports Save/Load operations for a project"""

    @abstractmethod
    def save(self, elements: list[model.BaseItem], filename: str = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self, filename: str = None) -> list[model.BaseItem]:
        raise NotImplementedError
