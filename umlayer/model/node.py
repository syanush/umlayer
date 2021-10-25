from uuid import UUID
from .element import Element


class Node:
    def __init__(self, element:Element, parent_id:UUID=None):
        self.element = element
        self.parent_id = parent_id

    def set_parent_id(self, parent_id:UUID):
        self.parent_id = parent_id
