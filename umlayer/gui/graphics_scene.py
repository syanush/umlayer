from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem

from . import constants, Settings, SceneLogic, BaseElement


class GraphicsScene(QGraphicsScene):
    def __init__(self, scene_logic: SceneLogic, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_grid()
        self._scene_logic: SceneLogic = scene_logic

    def notify(self):
        self._scene_logic.setDirty()

    def deselectAll(self):
        for item in self.selectedItems():
            item.setSelected(False)

    def init_grid(self):
        self.lines = []
        self.draw_grid()
        self._is_grid_visible = True
        self.set_grid_visible(False)
        # self.delete_grid()

    def draw_grid(self):
        X = self.sceneRect().x()
        Y = self.sceneRect().y()
        width = int(self.sceneRect().width())
        height = int(self.sceneRect().height())
        num_blocks_x = int(width / Settings.BLOCK_SIZE)
        num_blocks_y = int(height / Settings.BLOCK_SIZE)
        self.setItemIndexMethod(QGraphicsScene.NoIndex)

        pen = Settings.GRID_PEN

        small_z_value = -1e100

        for x in range(0, num_blocks_x + 1):
            xc = X + x * Settings.BLOCK_SIZE
            line = self.addLine(xc, Y, xc, height, pen)
            line.setZValue(small_z_value)
            self.lines.append(line)

        for y in range(0, num_blocks_y + 1):
            yc = Y + y * Settings.BLOCK_SIZE
            line = self.addLine(X, yc, width, yc, pen)
            line.setZValue(small_z_value)
            self.lines.append(line)

        for line in self.lines:
            line.setData(constants.ITEM_TYPE, "grid")

    def is_grid_visible(self):
        return self._is_grid_visible

    def set_grid_visible(self, visible=True):
        if self._is_grid_visible is visible:
            return
        self._is_grid_visible = visible
        for line in self.lines:
            line.setVisible(visible)

    def delete_grid(self):
        for line in self.lines:
            self.removeItem(line)
        del self.lines[:]

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Delete and event.modifiers() == Qt.NoModifier:
            self._scene_logic.delete_selected_elements()
        elif event.key() == Qt.Key_X and event.modifiers() == Qt.ControlModifier:
            self._scene_logic.cut_selected_elements()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self._scene_logic.copy_selected_elements()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self._scene_logic.paste_elements()

    def collidingElements(self, element):
        return self._filter_elements(element.collidingItems())

    def selectedElements(self) -> list[BaseElement]:
        selected_items = self.selectedItems()
        return self._filter_elements(selected_items)

    def elements(self) -> list[BaseElement]:
        return self._filter_elements(self.items())

    def clearElements(self) -> None:
        for element in self.elements():
            self.removeItem(element)

    def printItems(self):
        items = [
            item for item in self.items() if item.data(constants.ITEM_TYPE) != "grid"
        ]
        for i, item in enumerate(items):
            print(i, item)

    def _filter_elements(self, items: list[QGraphicsItem]) -> list[BaseElement]:
        return [item for item in items if isinstance(item, BaseElement)]

    def drawBackground(self, painter: QPainter, rect) -> None:
        super().drawBackground(painter, rect)
        # TODO: more effective grid?
        # create vector image of the grid
        # store it in an attribute
        # use it to redraw the grid at the background
