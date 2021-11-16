from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class PackageElement(QAbstractGraphicsShapeItem):
    padding = 5
    min2 = 20

    def __init__(self, dx: float = 0, dy: float = 0, parent=None) -> None:
        super().__init__(parent)

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        # self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # serializable data
        self._text1 = 'Package 1'
        self._text2 = '-Content 1\n+Content 2'
        self._dx = 0  # must be non-negative
        self._dy = 0
        # end of serializable data

        self._text_item1 = QGraphicsTextItem(self)
        self._text_item1.setFont(diagram_font)
        self._text_item1.setDefaultTextColor(Qt.black)
        self._text_item1.setPos(self.padding, self.padding)

        self._text_item2 = QGraphicsTextItem(self)
        self._text_item2.setFont(diagram_font)
        self._text_item2.setDefaultTextColor(Qt.black)

        self._recalculate()

    def _recalculate(self):
        self._text_item1.setPlainText(self._text1)
        self._text_item2.setPlainText(self._text2)
        br1 = self._text_item1.boundingRect()
        size1_x = br1.width() + 2 * self.padding
        size1_y = br1.height() + 2 * self.padding
        self._size1 = QPointF(size1_x, size1_y)
        self._text_item2.setPos(self.padding, self.padding + size1_y)
        br2 = self._text_item2.boundingRect()
        size2_x = max(br2.width() + 2 * self.padding + self._dx, size1_x + self.min2 + self._dx)
        size2_y = br2.height() + 2 * self.padding + self._dy
        self._size2 = QPointF(size2_x, size2_y)
        width = max(size1_x, size2_x)
        height = size1_y + size2_y
        self._bounding_rect = QRectF(0, 0, width, height)
        self._rect1 = QRectF(0, 0, size1_x, size1_y)
        self._rect2 = QRectF(0, size1_y, size2_x, size2_y)

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        x1 = self._size1.x()
        y1 = self._size1.y()
        x2 = self._size2.x()
        y2 = self._size2.y()
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(0, y1 + y2)
        path.lineTo(x2, y1 + y2)
        path.lineTo(x2, y1)
        path.lineTo(x1, y1)
        path.lineTo(x1, 0)
        path.lineTo(0, 0)
        return path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(item_pen)
        painter.setBrush(item_brush)
        painter.drawRect(self._rect1)
        painter.drawRect(self._rect2)

        if option.state & QStyle.State_Selected:
            painter.setPen(highlight_pen)
            painter.setBrush(highlight_brush)
            br = QPainterPath()
            br.addRect(self._bounding_rect)
            painter.fillPath(br, highlight_brush)
            painter.drawPath(self.shape())

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            print('selection', value)
        return super().itemChange(change, value)
