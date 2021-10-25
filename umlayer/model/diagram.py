"""Diagram
"""

from .element import Element


class Diagram(Element):
    def __init__(self, name:str="New diagram"):
        super().__init__(name)
