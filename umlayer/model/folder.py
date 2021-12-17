from uuid import UUID

from . import BaseItem, ProjectItemType


class Folder(BaseItem):
    def __init__(self, name: str = "New folder", parent_id: UUID = None):
        super().__init__(name, parent_id)

    @property
    def itemType(self) -> ProjectItemType:
        return ProjectItemType.FOLDER
