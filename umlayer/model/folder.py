from uuid import UUID

from .element import Element


class Folder(Element):
    def __init__(self, name: str = "New folder", parent_id: UUID = None):
        super().__init__(name, parent_id)
