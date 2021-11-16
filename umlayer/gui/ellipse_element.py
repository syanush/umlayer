from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class EllipseElement(QGraphicsItem):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

        # serializable data
        self._text = 'Use case'
        self._width = 150  # must be >= 10
        self._height = 50  # must be >= 10
        # end of serializable data

        self._lines = 'Use case 1'.split('\n')
        self._text_items = []
        for _ in self._lines:
            text_item = QGraphicsTextItem(self)
            text_item.setFont(diagram_font)
            text_item.setDefaultTextColor(item_color)
            self._text_items.append(text_item)

        self._recalculate()

    def _recalculate(self):
        text_width = 0.0
        text_height = 0.0
        n = len(self._lines)

        if n > 0:
            for i in range(n):
                line = self._lines[i]
                text_item = self._text_items[i]
                text_item.setPlainText(line)
                br = text_item.boundingRect()
                text_width = max(text_width, br.width())
                text_height += br.height()

            line_height = text_height / n

            for i in range(n):
                text_item = self._text_items[i]
                br = text_item.boundingRect()
                x = (self._width - br.width()) / 2
                y = (self._height - text_height) / 2 + line_height * i
                text_item.setPos(x, y)

        self._bounding_rect = QRectF(0, 0, self._width, self._height)

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addEllipse(self._bounding_rect)
        return path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(item_pen)
        painter.setBrush(item_brush)
        painter.drawEllipse(0, 0, self._width, self._height)

        if option.state & QStyle.State_Selected:
            painter.setPen(highlight_pen)
            painter.setBrush(highlight_brush)
            br = QPainterPath()
            br.addRect(self._bounding_rect)
            painter.fillPath(br, highlight_brush)
            painter.drawPath(self.shape())
