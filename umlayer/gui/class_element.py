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

        self._text_items = [TextItem(parent=self) for _ in range(3)]
        self._recalculate()

    def _make_rect(self, text_item) -> QRectF:
        br = text_item.boundingRect()
        width = br.width() + 2.0 * self.padding
        height = br.height() + 2.0 * self.padding
        rect = QRectF(0.0, 0.0, width, height)
        return rect

    def _recalculate(self):
        if len(self._texts) > 3:
            raise ValueError('len(self._texts) > 3')

        for text_item in self._text_items:
            text_item.setText('')
            text_item.setPos(0, 0)

        rects = []
        for text, text_item in zip(self._texts, self._text_items):
            text_item.setText(text)
            rect = self._make_rect(text_item)
            rects.append(rect)

        width = 2.0 * self.padding
        height = 2.0 * self.padding
        self._compartments = []

        if len(self._texts) > 0:
            width = max(compartment.width() for compartment in rects) + self._dx
            heights = [compartment.height() for compartment in rects]
            self._compartments.append(QRectF(0, 0, width, heights[0]))
        if len(self._texts) > 1:
            self._compartments.append(QRectF(0, heights[0], width, heights[1]))
        if len(self._texts) > 2:
            self._compartments.append(QRectF(0, heights[0] + heights[1], width, heights[2]))

        if len(self._texts) > 0:
            self._compartments[-1].adjust(0, 0, 0, self._dy)
            height = sum(rect.height() for rect in self._compartments)

        self._bounding_rect = QRectF(0, 0, width, height)

        for r, item in zip(self._compartments, self._text_items):
            item.setPos(r.x() + self.padding, r.y() + self.padding)

        self.update()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setPen(element_pen)
        painter.setBrush(element_brush)
        for compartment in self._compartments:
            painter.drawRect(compartment)

        if option.state & QStyle.State_Selected:
            painter.setPen(highlight_pen)
            painter.setBrush(highlight_brush)

            br = QPainterPath()
            br.addRect(self._bounding_rect)
            painter.fillPath(br, highlight_brush)

            painter.drawPath(self.shape())
