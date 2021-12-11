from PySide6.QtCore import QPointF
from PySide6.QtWidgets import (
    QGraphicsScene,
)


class Handler(object):
    def __init__(self, item) -> None:
        if item is None:
            raise ValueError("item")
        self._item = item
        self._handle = {}

    @property
    def handle(self):
        return self._handle

    def on_zvalue_change(self) -> None:
        for handle in self._handle.values():
            handle.setZValue(self._item.zValue() + 1.0)

    def selectAll(self, selected: bool = True) -> None:
        for handle in self._handle.values():
            handle.setSelected(selected)

    def is_handle_selected(self) -> bool:
        for handle in self._handle.values():
            if handle.isSelected():
                return True
        return False

    def on_scene_change(self, scene: QGraphicsScene) -> None:
        for handle in self._handle.values():
            if scene is None:
                # the scene is about to disappear
                self._item.scene().removeItem(handle)
            else:
                # new scene
                scene.addItem(handle)

    def moveBy(self, delta: QPointF) -> None:
        for handle in self._handle.values():
            handle.moveBy(delta.x(), delta.y())

    def setLive(self, is_live: bool) -> None:
        for handle in self._handle.values():
            handle.setLive(is_live)

    def isResizing(self) -> bool:
        if not self._handle:
            return False
        return 1 == sum(int(handle.isSelected()) for handle in self._handle.values())
