"""Diagrams belong to a project"""

from uuid import UUID
from .element import Element


class Project:
    def __init__(self):
        self.elements = {}
        self.root = None
        self.is_dirty = False

    def setRoot(self, root: Element):
        self._add(root)
        self.root = root

    def remove(self, element_id: UUID = None):
        if element_id not in self.elements.keys():
            raise AttributeError("element_id")
        self._remove(element_id)
        self.is_dirty = True

    def _remove(self, element_id: UUID = None):
        for child in self.children(element_id):
            self._remove(child.id)
        del self.elements[element_id]

    def add(self, element: Element, parent_id: UUID = None):
        if parent_id not in self.elements.keys():
            raise AttributeError("parent_id")
        self._add(element, parent_id)
        self.is_dirty = True

    def _add(self, element: Element, parent_id: UUID = None):
        element.parent_id = parent_id
        self.elements[element.id] = element

    def get(self, element_id: UUID) -> Element:
        return self.elements[element_id]

    def children(self, parent_id: UUID) -> set[Element]:
        return set(element for element in self.elements.values() if element.parent_id == parent_id)
