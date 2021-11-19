"""Scene Editor

"""

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class GraphicsView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSceneRect(-1000, -1000, 2000, 2000)
        # self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        # self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setRubberBandSelectionMode(Qt.ItemSelectionMode.ContainsItemBoundingRect)

    def getMainWindow(self):
        return self.parent().parent()

    def mouseMoveEvent(self, e: QMouseEvent):
        if e.buttons() & Qt.LeftButton:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setRubberBandSelectionMode(Qt.ContainsItemBoundingRect)
        elif e.buttons() & Qt.RightButton:
            pass
            # main_window.sceneView.setDragMode(QGraphicsView.ScrollHandDrag)

        super().mouseMoveEvent(e)
