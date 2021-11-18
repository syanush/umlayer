import logging

from PySide6.QtWidgets import *

from . import *


class GraphicsScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def addUserElement(self, x: float, y: float):
        logging.info('Add user element')
        item = UserElement()
        item.setPos(x, y)
        self.addItem(item)

    def addUseCase(self):
        item = UseCaseElement(20, 20, 100, 50)
        self.addItem(item)

    def addPackageElement(self, x: float, y: float):
        item = PackageElement()
        item.setPos(x, y)
        self.addItem(item)

    def addEllipseElement(self, x: float, y: float):
        item = EllipseElement()
        item.setPos(x, y)
        self.addItem(item)

    def addNoteElement(self, x: float, y: float):
        item = NoteElement('Note..')
        item.setPos(x, y)
        self.addItem(item)

    def addTextElement(self, x: float, y: float):
        item = TextElement('Left-aligned\ntext')
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        item.setFlag(QGraphicsItem.ItemIsMovable, True)
        item.setPos(x, y)
        self.addItem(item)

    def addCenteredTextElement(self, x: float, y: float):
        item = TextItem('Centered\ntext', center=True)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        item.setFlag(QGraphicsItem.ItemIsMovable, True)
        item.setPos(x, y)
        self.addItem(item)

    def addSimpleClassElement(self, x: float, y: float):
        item = ClassElement(['SimpleClass'], 100, 50)
        item.setPos(x, y)
        self.addItem(item)

    def addFatClassElement(self, x: float, y: float):
        item = ClassElement([
            'FatClass',
            '-task_name',
            '+set_task_name(name: string)\n+run_asynchronously(monitor: Monitor)'
        ], 100, 50)
        item.setPos(x, y)
        self.addItem(item)

    def addLineElement(self, x: float, y: float):
        item = LineElement()
        item.setPos(x, y)
        self.addItem(item)

    def addHandleElement(self, x: float, y: float):
        item = HandleElement()
        item.setPos(x, y)
        self.addItem(item)