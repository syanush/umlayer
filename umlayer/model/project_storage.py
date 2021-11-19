"""Persistent storage for a project
"""

from abc import ABC, abstractmethod

from . import Element


class ProjectStorage(ABC):
    """It supports Save/Load operations for a project
    """

    @abstractmethod
    def save(self, elements: list[Element], filename: str = None):
        raise NotImplementedError

    @abstractmethod
    def load(self, filename: str = None) -> list[Element]:
        raise NotImplementedError
