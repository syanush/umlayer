from uuid import UUID

from . import BaseItem


class Folder(BaseItem):
    def __init__(self, name: str = "New folder", parent_id: UUID = None):
        super().__init__(name, parent_id)
