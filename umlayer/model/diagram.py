"""Diagram
"""

from uuid import UUID

from . import BaseItem


class Diagram(BaseItem):
    def __init__(self, name: str = "New diagram", parent_id: UUID = None):
        super().__init__(name, parent_id)
        self.dtos = []
        self.scroll_data = None
