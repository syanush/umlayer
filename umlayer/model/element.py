import uuid


class Element:
    def __init__(self, name:str="New element"):
        self.name = name
        self.id = uuid.uuid4()
