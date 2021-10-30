"""Persistent storage for a project
"""

from abc import ABC, abstractmethod

from .element import Element


class ProjectStorage(ABC):
    """It supports Save/Load operations for a project

    Internally, .ulr file is SQLite database, with such tables as:

    -  elements: the representation of the project tree elements,
    such as folders and diagrams, including parent id

    """

    @abstractmethod
    def save(self, elements: list[Element], filename: str = None):
        raise NotImplementedError

    @abstractmethod
    def load(self, filename: str = None) -> list[Element]:
        raise NotImplementedError
