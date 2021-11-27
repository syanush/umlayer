from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class GraphicsScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_grid()

    @property
    def window(self):
        return self.parent()

    def deselectAll(self):
        for item in self.selectedItems():
            item.setSelected(False)

    def init_grid(self):
        self.lines = []
        self.draw_grid()
        # self.set_grid_visible(False)
        # self.delete_grid()

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

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Delete and event.modifiers() == Qt.NoModifier:
            self.window.scene_logic.delete_selected_elements()
        elif event.key() == Qt.Key_X and event.modifiers() == Qt.ControlModifier:
            self.window.scene_logic.cut_selected_elements()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self.window.scene_logic.copy_selected_elements()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self.window.scene_logic.paste_elements()

    def selectedElements(self):
        return self._filter_elements(self.selectedItems())

    def elements(self):
        return self._filter_elements(self.items())

    def clearElements(self):
        for element in self.elements():
            self.removeItem(element)

    def printItems(self):
        items = [item for item in self.items()
                 if item.data(ITEM_TYPE) != 'grid']
        for i, item in enumerate(items):
            print(i, item)

    def _filter_elements(self, items):
        return [item for item in items
                if isinstance(item, BaseElement)]
