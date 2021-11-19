from PySide6.QtCore import *
from PySide6.QtWidgets import *

from . import *


class HandleItem(QGraphicsObject):
    size = 10
    position_changed_signal = Signal(QPointF)
    selection_changed_signal = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self._bounding_rect = QRectF(-self.size, -self.size, 2 * self.size, 2 * self.size)
        self._is_live = False

    def setLive(self, is_live):
        self._is_live = is_live
        self.update()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addEllipse(self._bounding_rect)
        return path

    normal_pen = QPen(Qt.black, 1)
    selected_pen = QPen(Qt.blue, 1)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        if not self._is_live:
            return
        painter.setRenderHint(QPainter.Antialiasing)
        is_selected = self.isSelected() # option.state & QStyle.State_Selected
        pen = self.selected_pen if is_selected else self.normal_pen
        painter.setPen(pen)
        brush = highlight_brush if is_selected else element_brush
        painter.setBrush(brush)
        painter.drawEllipse(self._bounding_rect)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            is_selected = bool(value)
            self.selection_changed_signal.emit(is_selected)
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.position_changed_signal.emit(value)
        return super().itemChange(change, value)
