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
        self.onFocused(False)

    @property
    def window(self):
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

    def scrollData(self):
        h: QScrollBar = self.horizontalScrollBar()
        v: QScrollBar = self.verticalScrollBar()
        return h.value(), h.minimum(), h.maximum(), v.value(), v.minimum(), v.maximum()

    def setScrollData(self, hv, hmin, hmax, vv, vmin, vmax):
        h: QScrollBar = self.horizontalScrollBar()
        v: QScrollBar = self.verticalScrollBar()
        h.setMinimum(hmin)
        h.setMaximum(hmax)
        h.setValue(hv)
        v.setMinimum(vmin)
        v.setMaximum(vmax)
        v.setValue(vv)

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

    def focusInEvent(self, event: QFocusEvent) -> None:
        self.onFocused(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        self.onFocused(False)
        super().focusOutEvent(event)

    def onFocused(self, is_focused: bool) -> None:
        self.setFrameStyle(QFrame.Panel | (QFrame.Plain if is_focused else QFrame.Sunken))

    def scale_changed(self, scale):
        new_scale = int(scale[:-1]) / 100.0
        old_matrix = self.transform()
        self.resetTransform()
        self.translate(old_matrix.dx(), old_matrix.dy())
        self.scale(new_scale, new_scale)
