from PySide6.QtCore import *
from PySide6.QtWidgets import *

from . import *


class ClassElement(QAbstractGraphicsShapeItem):
    padding = 5

    def __init__(self, texts: list[str],
                 dx: float = 0, dy: float = 0, parent=None) -> None:
        super().__init__(parent)

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        # self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # serializable data
        self._texts = texts
        self._dx = dx  # must be non-negative
        self._dy = dy
        # end of serializable data

        self._text_items = []
        self._recalculate()

    def _make_text_item(self, text) -> QGraphicsTextItem:
        text_item = QGraphicsTextItem(self)
        text_item.setFont(diagram_font)
        text_item.setDefaultTextColor(Qt.black)
        text_item.setPlainText(text)
        return text_item

    def _make_rect(self, text_item) -> QRectF:
        br = text_item.boundingRect()
        width = br.width() + 2.0 * self.padding
        height = br.height() + 2.0 * self.padding
        rect = QRectF(0.0, 0.0, width, height)
        return rect

    def _recalculate(self):
        for item in self._text_items:
            if item.scene():
                item.setParent(None)
                item.scene().removeItem(item)

        self._text_items = []
        rects = []

        if len(self._texts) > 3:
            raise ValueError('len(self._texts) > 3')

        for text in self._texts:
            text_item = self._make_text_item(text)
            self._text_items.append(text_item)
            rect = self._make_rect(text_item)
            rects.append(rect)

        width = 2.0 * self.padding
        height = 2.0 * self.padding
        self._rects = []

        if len(self._texts) > 0:
            width = max(r.width() for r in rects) + self._dx
            heights = [r.height() for r in rects]
            self._rects.append(QRectF(0, 0, width, heights[0]))
        if len(self._texts) > 1:
            self._rects.append(QRectF(0, heights[0], width, heights[1]))
        if len(self._texts) > 2:
            self._rects.append(QRectF(0, heights[0] + heights[1], width, heights[2]))

        if len(self._texts) > 0:
            self._rects[-1].adjust(0, 0, 0, self._dy)
            height = sum(rect.height() for rect in self._rects)

        self._bounding_rect = QRectF(0, 0, width, height)

        for item, r in zip(self._text_items, self._rects):
            item.setPos(r.x() + self.padding, r.y() + self.padding)

        self.update()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setPen(item_pen)
        painter.setBrush(item_brush)
        for rect in self._rects:
            painter.drawRect(rect)

        if option.state & QStyle.State_Selected:
            painter.setPen(highlight_pen)
            painter.setBrush(highlight_brush)

            br = QPainterPath()
            br.addRect(self._bounding_rect)
            painter.fillPath(br, highlight_brush)

            painter.drawPath(self.shape())
