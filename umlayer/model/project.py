"""Diagrams belong to a project"""

import jsonpickle

from uuid import UUID
from .element import Element
from .node import Node


class Project:
    def __init__(self):
        self.nodes = {}
        self.root = None
        self.is_dirty = False

    def setRoot(self, root:Element):
        self._add(root)
        self.root = root

    def remove(self, element_id:UUID=None):
        if element_id not in self.nodes.keys():
            raise AttributeError("element_id")
        self._remove(element_id)
        self.is_dirty = True

    def _remove(self, element_id:UUID=None):
        for child in self.children(element_id):
            self._remove(child.id)
        del self.nodes[element_id]

    def add(self, element:Element, parent_id:UUID=None):
        if parent_id not in self.nodes.keys():
            raise AttributeError("parent_id")
        self._add(element, parent_id)
        self.is_dirty = True

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

        if filename is None:
            raise ValueError('filename is None')

        for element_id, node in self.nodes.items():
            element = node.element
            parent_id = node.parent_id
            str_json = jsonpickle.encode(element)
            print(f'{str(element_id)} {str(parent_id)} {str_json}')

        self.is_dirty = False

    def load(self, filename: str):
        """Loads project data and settings from a file

         Throws exceptions in case of errors
         """
        # jsonpickle.decode(frozen)
        self.is_dirty = False
