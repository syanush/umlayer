from PySide6.QtWidgets import *

from . import *


class GraphicsScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def addActorElement(self, x: float, y: float):
        item = ActorElement('Actor')
        item.setPos(x, y)
        self.addItem(item)

    def addPackageElement(self, x: float, y: float):
        item = PackageElement('Package 1\n--\nFunctional\nPerformant')
        item.setPos(x, y)
        self.addItem(item)

    def addEllipseElement(self, x: float, y: float):
        item = EllipseElement(150, 50, 'Use Case 1')
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
        item = TextElement('Centered\ntext', center=True)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        item.setFlag(QGraphicsItem.ItemIsMovable, True)
        item.setPos(x, y)
        self.addItem(item)

    def addSimpleClassElement(self, x: float, y: float):
        item = ClassElement('SimpleClass')
        item.setPos(x, y)
        self.addItem(item)

    def addFatClassElement(self, x: float, y: float):
        text = '''FatClass
--
-task_name
--
+set_task_name(name: string)\n+run_asynchronously(monitor: Monitor)'''

        item = ClassElement(text)
        item.setPos(x, y)
        self.addItem(item)

    def addLineElement(self, x: float, y: float):
        item = LineElement()
        item.setPos(x, y)
        self.addItem(item)

    def addHandleElement(self, x: float, y: float):
        item = HandleItem()
        item.setPos(x, y)
        self.addItem(item)
