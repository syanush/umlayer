from PySide6.QtCore import *
from PySide6.QtWidgets import *

from . import *


class LineElement(QGraphicsItem):
    diameter = 40

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

        self._point1 = QPointF(0, 0)
        self._point2 = QPointF(100, 100)

        self._handle1 = HandleItem(10, parent=self)
        self._handle1.setPos(self._point1)
        self._handle1.position_changed_signal.connect(self._handle1_position_changed)
        self._handle1.selection_changed_signal.connect(self._handle_selection_changed)
        self._handle1.setSelected(False)

        self._handle2 = HandleItem(10, parent=self)
        self._handle2.setPos(self._point2)
        self._handle2.position_changed_signal.connect(self._handle2_position_changed)
        self._handle2.selection_changed_signal.connect(self._handle_selection_changed)
        self._handle2.setSelected(False)

        self.stroker = QPainterPathStroker()
        self.stroker.setWidth(15)

        self.setLive(False)
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

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        return self._shape_path

    normal_pen = QPen(Qt.black, 1.2)
    selected_pen = QPen(Qt.blue, 1.2)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        pen = self.selected_pen if self.isSelected() else self.normal_pen
        painter.setPen(pen)
        point1 = self._point1
        point2 = self._point2
        x1 = point1.x()
        y1 = point1.y()
        x2 = point2.x()
        y2 = point2.y()
        painter.drawLine(x1, y1, x2, y2)
        # painter.drawPath(self.shape())

    def setLive(self, is_live):
        self._is_live = is_live
        self._handle1.setLive(is_live)
        self._handle2.setLive(is_live)
        self._recalculate()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            is_selected = bool(value)
            print('Line selection', is_selected)
            self.prepareGeometryChange()
            self.setLive(is_selected)
        return super().itemChange(change, value)
