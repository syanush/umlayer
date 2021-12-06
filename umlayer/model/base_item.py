from abc import ABC
from uuid import UUID, uuid4

from . import ProjectItemType


class BaseItem(ABC):
    def __init__(self, name: str = None, parent_id: UUID = None):
        self._name = name or ''
        self.parent_id = parent_id
        self.id = uuid4()

    @property
    def item_type(self) -> ProjectItemType:
        raise NotImplementedError

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name
