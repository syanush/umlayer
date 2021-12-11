from PySide6.QtCore import QPointF, QRectF, Signal
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import (
    QGraphicsItem,
    QStyleOptionGraphicsItem,
    QGraphicsObject,
)

from . import gui_utils, Settings


class ResizeHandleItem(QGraphicsObject):
    position_change_signal = Signal(QPointF)
    position_changed_signal = Signal(QPointF)
    selection_changed_signal = Signal(bool)

    def __init__(
        self, size: int, calculateHandlePositionChange, name: str = "", parent=None
    ):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.size = size
        self._calculateHandlePositionChange = calculateHandlePositionChange
        self._name = name
        self._bounding_rect = QRectF(
            -self.size, -self.size, 2 * self.size, 2 * self.size
        )
        path = QPainterPath()
        path.addEllipse(self._bounding_rect)
        self._shape_path = path
        self._is_live = False
        self._isPositionChangeAccepted = False

    def __str__(self):
        return f"<Handle {self._name} size={self.size}: {self.pos().x()}, {self.pos().y()}>"

    def isPositionChangeAccepted(self) -> bool:
        return self._isPositionChangeAccepted

    def setPositionChangeAccepted(self, accepted: bool) -> None:
        self._isPositionChangeAccepted = accepted

    def setLive(self, is_live):
        self._is_live = is_live
        self.update()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        return self._shape_path

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None
    ) -> None:
        if not self._is_live:
            return
        pen = (
            Settings.HANDLE_SELECTED_PEN
            if self.isSelected()
            else Settings.HANDLE_NORMAL_PEN
        )
        brush = (
            Settings.RESIZE_HANDLE_SELECTED_BRUSH
            if self.isSelected()
            else Settings.RESIZE_HANDLE_NORMAL_BRUSH
        )
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self._bounding_rect)

    def itemChange(self, change, value):
        if self.scene() and change == QGraphicsItem.ItemPositionChange:
            value = self.calculateItemPositionChange(value)
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.onItemSelectedHasChanged(value)
        return super().itemChange(change, value)

    def calculateItemPositionChange(self, position):
        snapped_position = gui_utils.snap_position(position)
        result_position = self._calculateHandlePositionChange(self, snapped_position)
        return result_position

    def onItemSelectedHasChanged(self, value):
        is_selected = bool(value)
        self.selection_changed_signal.emit(is_selected)
