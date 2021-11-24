from uuid import UUID

from . import Element


class Project:
    def __init__(self):
        self.elements = {}
        self.root = None
        self._is_dirty = False

    def dirty(self):
        return self._is_dirty

    def setDirty(self, dirty):
        # print(f'{self._is_dirty=}')
        self._is_dirty = dirty

    def setRoot(self, root: Element):
        self._add(root)
        self.root = root

    def remove(self, element_id: UUID = None):
        if element_id not in self.elements.keys():
            raise AttributeError("element_id")
        self._remove(element_id)
        self.setDirty(True)

    def _remove(self, element_id: UUID = None):
        for child in self.children(element_id):
            self._remove(child.id)
        del self.elements[element_id]

    def add(self, element: Element, parent_id: UUID = None):
        if parent_id not in self.elements.keys():
            raise AttributeError("parent_id")
        self._add(element, parent_id)
        self.setDirty(True)

    def _add(self, element: Element, parent_id: UUID = None):
        element.parent_id = parent_id
        self.elements[element.id] = element

    def get(self, element_id: UUID) -> Element:
        return self.elements.get(element_id)

    def children(self, parent_id: UUID) -> set[Element]:
        return set(element for element in self.elements.values() if element.parent_id == parent_id)

    def count(self):
        return len(self.elements)

    def printElements(self):
        """Debugging feature"""
        for element in self.elements.values():
            print(f'{element.name}   {element.id}')
        print()
