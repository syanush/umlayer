"""GraphicsView
"""

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class GraphicsView(QGraphicsView):

    def getMainWindow(self):
        return self.parent().parent()

    def mouseMoveEvent(self, e: QMouseEvent):
        main_window = self.getMainWindow()
        if e.buttons() & Qt.LeftButton:
            main_window.sceneView.setDragMode(QGraphicsView.RubberBandDrag)
            main_window.sceneView.setRubberBandSelectionMode(Qt.ContainsItemBoundingRect)
        elif e.buttons() & Qt.RightButton:
            main_window.sceneView.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mouseMoveEvent(e)
        #print(e.pos())
        #message = f'sceneRect={self.scene.sceneRect()}'
        #self.aStatusBar.showMessage(message)
