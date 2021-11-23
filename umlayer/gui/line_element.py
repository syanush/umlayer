from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class LineElement(QGraphicsItem, BaseElement):
    def __init__(self, x1: float = 0, y1: float = 0, x2: float = 100, y2: float = 100, parent=None):
        super().__init__(parent)
        super(BaseElement, self).__init__()
        self._abilities = set()
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self._point1 = QPointF(x1, y1)
        self._point2 = QPointF(x2, y2)

        self._handle1 = HandleItem(10, parent=self)
        self._handle1.position_changed_signal.connect(self._handle1_position_changed)
        self._handle1.selection_changed_signal.connect(self._handle_selection_changed)
        self._handle1.setSelected(False)

        self._handle2 = HandleItem(10, parent=self)
        self._handle2.position_changed_signal.connect(self._handle2_position_changed)
        self._handle2.selection_changed_signal.connect(self._handle_selection_changed)
        self._handle2.setSelected(False)

        self.stroker = QPainterPathStroker()
        self.stroker.setWidth(15)

        self.setLive(False)
        self._recalculate()

    def toDto(self):
        dto = super().toDto()
        dto['x1'] = self._point1.x()
        dto['y1'] = self._point1.y()
        dto['x2'] = self._point2.x()
        dto['y2'] = self._point2.y()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self._point1 = QPointF(dto['x1'], dto['y1'])
        self._point2 = QPointF(dto['x2'], dto['y2'])
        self._recalculate()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        return self._shape_path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        pen = Settings.LINE_SELECTED_PEN if self.isSelected() else Settings.LINE_NORMAL_PEN
        painter.setPen(pen)
        point1 = self._point1
        point2 = self._point2
        x1 = point1.x()
        y1 = point1.y()
        x2 = point2.x()
        y2 = point2.y()
        painter.drawLine(x1, y1, x2, y2)
        # painter.drawPath(self.shape())

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if self.scene() and \
                change == QGraphicsItem.ItemPositionChange and \
                QApplication.mouseButtons() == Qt.LeftButton:
            return QPointF(gui_utils.snap(value.x()), gui_utils.snap(value.y()))
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            is_selected = bool(value)
            self.prepareGeometryChange()
            self.setLive(is_selected)
        return super().itemChange(change, value)

    def setLive(self, is_live):
        self._is_live = is_live
        self._handle1.setLive(is_live)
        self._handle2.setLive(is_live)
        self._recalculate()

    def _handle_selection_changed(self, is_selected):
        self.setLive(is_selected)

    def _handle1_position_changed(self, point):
        self._point1 = point
        self._recalculate()

    def _handle2_position_changed(self, point):
        self._point2 = point
        self._recalculate()

    def _recalculate(self):
        self.prepareGeometryChange()
        self._handle1.setPos(self._point1)
        self._handle2.setPos(self._point2)

        x1 = self._point1.x()
        y1 = self._point1.y()
        x2 = self._point2.x()
        y2 = self._point2.y()
        # IMPORTANT: width and height of the bounding box must be non-negative,
        # to remove painting artifacts
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x1 - x2)
        h = abs(y1 - y2)
        self._bounding_rect = QRectF(x, y, w, h)

        path = QPainterPath()
        path.moveTo(self._handle1.pos())
        path.lineTo(self._handle2.pos())
        path.lineTo(self._handle1.pos())
        self._shape_path = self.stroker.createStroke(path)

        self.update()
