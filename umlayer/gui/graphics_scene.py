from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class GraphicsScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lines = []
        self.draw_grid()
        self.set_grid_opacity(0.2)
        # self.set_grid_visible(False)
        # self.delete_grid()

    @property
    def window(self):
        return self.parent()

    def deselectAll(self):
        for item in self.selectedItems():
            item.setSelected(False)

    def draw_grid(self):
        X = self.sceneRect().x()
        Y = self.sceneRect().y()
        width = int(self.sceneRect().width())
        height = int(self.sceneRect().height())
        num_blocks_x = int(width / Settings.BLOCK_SIZE)
        num_blocks_y = int(height / Settings.BLOCK_SIZE)
        self.setItemIndexMethod(QGraphicsScene.NoIndex)  # Is it devastating for the app?

        pen = Settings.GRID_PEN

        for x in range(0, num_blocks_x + 1):
            xc = X + x * Settings.BLOCK_SIZE
            self.lines.append(self.addLine(xc, Y, xc, height, pen))

        for y in range(0, num_blocks_y + 1):
            yc = Y + y * Settings.BLOCK_SIZE
            self.lines.append(self.addLine(X, yc, width, yc, pen))

        for line in self.lines:
            line.setData(ITEM_TYPE, 'grid')

    def set_grid_visible(self, visible=True):
        for line in self.lines:
            line.setVisible(visible)

    def delete_grid(self):
        for line in self.lines:
            self.removeItem(line)
        del self.lines[:]

    def set_grid_opacity(self, opacity):
        for line in self.lines:
            line.setOpacity(opacity)

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
        item.setPos(x, y)
        self.addItem(item)

    def addCenteredTextElement(self, x: float, y: float):
        item = TextElement('Centered\ntext', center=True)
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

    def addHandleItem(self, x: float, y: float):
        item = HandleItem(10)
        item.setLive(True)
        item.setPos(x, y)
        self.addItem(item)

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Delete and event.modifiers() == Qt.NoModifier:
            self.window.logic.delete_selected_elements()
        elif event.key() == Qt.Key_X and event.modifiers() == Qt.ControlModifier:
            self.window.logic.cut_selected_elements()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self.window.logic.copy_selected_elements()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self.window.logic.paste_elements()

    def printItems(self):
        items = [item for item in self.items()
                 if item.data(ITEM_TYPE) != 'grid']
        for i, item in enumerate(items):
            print(i, item)
