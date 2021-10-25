"""Diagrams belong to a project"""

from uuid import UUID
from .element import Element
from .node import Node


class Project:
    def __init__(self):
        self.nodes = {}
        self.root = None

    def setRoot(self, root:Element):
        self._add(root)
        self.root = root

    def add(self, element:Element, parent_id:UUID=None):
        if parent_id not in self.nodes.keys():
            raise AttributeError("parent_id")
        self._add(element, parent_id)

    def _add(self, element:Element, parent_id:UUID=None):
        node = Node(element, parent_id)
        self.nodes[element.id] = node

    def get(self, element_id:UUID) -> Element:
        return self.nodes[element_id].element

    def children(self, parent_id:UUID) -> set[Element]:
        return set(node.element for node in self.nodes.values() if node.parent_id == parent_id)

    def save(self, filename: str):
        """Saves project data and settings to a file

        Throws exceptions in case of errors
        """
        pass

    def load(self, filename: str):
        """Loads project data and settings from a file

         Throws exceptions in case of errors
         """
        pass
