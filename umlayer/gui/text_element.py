from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class TextElement(QGraphicsItem):
    def __init__(self, text, center: bool = False, parent=None) -> None:
        super().__init__(parent)

        # serializable data
        self._text = text
        self._center = center
        # end of serializable data

        self._text_items = []
        self._recalculate()

    def setText(self, text: str):
        self._text = text
        self._recalculate()

    def setCenter(self, center: bool):
        self._center = center
        self._recalculate()

    def _recalculate(self):
        for item in self._text_items:
            if item.scene():
                item.setParent(None)
                item.scene().removeItem(item)

        self._lines = self._text.split('\n')
        self._text_items = []

        for _ in self._lines:
            text_item = QGraphicsTextItem(self)
            text_item.setFont(diagram_font)
            text_item.setDefaultTextColor(item_color)
            self._text_items.append(text_item)

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
                if self._center:
                    x = (text_width - br.width()) / 2
                else:
                    x = 0
                y = line_height * i
                text_item.setPos(x, y)

        self._bounding_rect = QRectF(0, 0, text_width, text_height)

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        if option.state & QStyle.State_Selected:
            painter.setPen(highlight_pen)
            painter.setBrush(highlight_brush)

            br = QPainterPath()
            br.addRect(self._bounding_rect)
            painter.fillPath(br, highlight_brush)

            painter.drawPath(self.shape())
