from abc import ABC
from uuid import UUID, uuid4


class Element(ABC):
    def __init__(self, name: str = "New element", parent_id: UUID = None):
        self.name = name
        self.parent_id = parent_id
        self.id = uuid4()
