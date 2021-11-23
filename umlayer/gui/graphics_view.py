"""Scene Editor

"""

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class GraphicsView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setRubberBandSelection()

    def getMainWindow(self):
        # TODO: more robust method?
        return self.parent().parent()

    def setPanning(self):
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setInteractive(False)
        # self.setCursor(Qt.ClosedHandCursor)

    def setRubberBandSelection(self):
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setRubberBandSelectionMode(Qt.ItemSelectionMode.ContainsItemBoundingRect)
        self.setInteractive(True)
        # self.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            # Must precede fake event handling
            self.setPanning()
            fake = QMouseEvent(event.type(), event.pos(), Qt.LeftButton, event.buttons(), event.modifiers())
            super().mousePressEvent(fake)
            # print('middle button pressed', self.isInteractive(), self.dragMode())
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            fake = QMouseEvent(event.type(), event.pos(), Qt.LeftButton, event.buttons(), event.modifiers())
            super().mouseReleaseEvent(fake)
            # Must follow fake event handling
            self.setRubberBandSelection()
            # print('middle button released', self.isInteractive(), self.dragMode())
            return
        super().mouseReleaseEvent(event)
