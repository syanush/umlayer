from abc import ABC
from uuid import UUID, uuid4


class BaseItem(ABC):
    def __init__(self, name: str = None, parent_id: UUID = None):
        self._name = name or ''
        self.parent_id = parent_id
        self.id = uuid4()

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

