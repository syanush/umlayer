from .element import Element


class Folder(Element):
    def __init__(self, name:str="New folder"):
        super().__init__(name)
