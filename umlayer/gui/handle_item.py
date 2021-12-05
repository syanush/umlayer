from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class HandleItem(QGraphicsObject):
    position_changed_signal = Signal(QPointF)
    selection_changed_signal = Signal(bool)

    def __init__(self, size: int, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.size = size
        self._bounding_rect = QRectF(-self.size, -self.size, 2 * self.size, 2 * self.size)
        path = QPainterPath()
        path.addEllipse(self._bounding_rect)
        self._shape_path = path
        self._is_live = False

    def __str__(self):
        return f'<Handle {self.size}: {self.pos().x()}, {self.pos().y()}>'

    def setLive(self, is_live):
        self._is_live = is_live
        self.update()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        return self._shape_path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        if not self._is_live:
            return
        pen = Settings.HANDLE_SELECTED_PEN if self.isSelected() else Settings.HANDLE_NORMAL_PEN
        painter.setPen(pen)
        painter.drawEllipse(self._bounding_rect)

    def itemChange(self, change, value):
        if self.scene() and \
                change == QGraphicsItem.ItemPositionChange and \
                QApplication.mouseButtons() == Qt.LeftButton:
            return QPointF(gui_utils.snap(value.x()), gui_utils.snap(value.y()))
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.position_changed_signal.emit(value)
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            is_selected = bool(value)
            self.selection_changed_signal.emit(is_selected)
        return super().itemChange(change, value)
