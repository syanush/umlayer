"""Diagram
"""

from uuid import UUID

from . import Element


class Diagram(Element):
    def __init__(self, name: str = "New diagram", parent_id: UUID = None):
        super().__init__(name, parent_id)
