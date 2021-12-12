"""Scene Editor

"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QFocusEvent, QWheelEvent
from PySide6.QtWidgets import QFrame, QScrollBar, QGraphicsView


class GraphicsView(QGraphicsView):
    step_ticks = 120

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setRubberBandSelection()
        self.onFocused(False)
        self.last_ticks: int = 0
        self.current_ticks: int = 0

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

    def setScrollData(self, h_val, h_min, h_max, v_val, v_min, v_max):
        h: QScrollBar = self.horizontalScrollBar()
        v: QScrollBar = self.verticalScrollBar()
        h.setMinimum(h_min)
        h.setMaximum(h_max)
        h.setValue(h_val)
        v.setMinimum(v_min)
        v.setMaximum(v_max)
        v.setValue(v_val)

    panMouseButton = Qt.RightButton

    def mousePressEvent(self, event):
        if event.button() == self.panMouseButton:
            # Must precede fake event handling
            self.setPanning()
            fake = QMouseEvent(
                event.type(),
                event.pos(),
                Qt.LeftButton,
                event.buttons(),
                event.modifiers(),
            )
            super().mousePressEvent(fake)
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == self.panMouseButton:
            fake = QMouseEvent(
                event.type(),
                event.pos(),
                Qt.LeftButton,
                event.buttons(),
                event.modifiers(),
            )
            super().mouseReleaseEvent(fake)
            # Must follow fake event handling
            self.setRubberBandSelection()
            return
        super().mouseReleaseEvent(event)

    def focusInEvent(self, event: QFocusEvent) -> None:
        self.onFocused(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        self.onFocused(False)
        super().focusOutEvent(event)

    def onFocused(self, is_focused: bool) -> None:
        self.setFrameStyle(
            QFrame.Panel | (QFrame.Plain if is_focused else QFrame.Sunken)
        )

    def scale_changed(self, scale):
        new_scale = int(scale[:-1]) / 100.0
        old_matrix = self.transform()
        self.resetTransform()
        self.translate(old_matrix.dx(), old_matrix.dy())
        self.scale(new_scale, new_scale)

    def wheelEvent(self, event: QWheelEvent) -> None:
        self.current_ticks += event.angleDelta().y()
        while self.current_ticks >= self.last_ticks + self.step_ticks:
            self.last_ticks += self.step_ticks
            self.window.zoom(1)
        while self.current_ticks <= self.last_ticks - self.step_ticks:
            self.last_ticks -= self.step_ticks
            self.window.zoom(-1)
        event.accept()
