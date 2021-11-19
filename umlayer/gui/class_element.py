import re

from PySide6.QtCore import *
from PySide6.QtWidgets import *

from . import *


class ClassElement(QAbstractGraphicsShapeItem):
    padding = 5

    def __init__(self, text: str = '', dx: float = 0, dy: float = 0, parent=None) -> None:
        super().__init__(parent)

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

        # serializable data
        self._text = text or ''
        self._dx = dx  # must be non-negative
        self._dy = dy
        # end of serializable data

        self._text_items = []
        self._recalculate()

    def _get_rect(self, item: TextItem) -> QRectF:
        br = item.boundingRect()
        width = br.width() + 2.0 * self.padding
        height = br.height() + 2.0 * self.padding
        rect = QRectF(0.0, 0.0, width, height)
        return rect

    def _deleteTextItems(self) -> None:
        """Delete old text items"""
        for item in self._text_items:
            if item.scene():
                item.setParent(None)
                item.scene().removeItem(item)
        self._text_items = []

    def _createTextItems(self) -> list[TextItem]:
        """Create text item for every text section"""
        n = len(self._texts)
        items = []
        for i in range(n):
            text = self._texts[i]
            center = True if i == 0 else False
            item = TextItem(text, center=center, parent=self)
            items.append(item)
        return items

    def _getMaxWidth(self) -> float:
        """Return the maximal width of the text items"""
        n = len(self._texts)
        width = 2.0 * self.padding if n == 0 else \
            max(self._get_rect(item).width() for item in self._text_items)
        return width

    def _createCompartments(self, width: float) -> list[QRectF]:
        """Create compartments with the same width"""
        n = len(self._texts)
        compartments = []
        height = 0  #
        for i in range(n):
            item = self._text_items[i]
            rect = self._get_rect(item)
            compartment = QRectF(0, height, width, rect.height())

            if i == 0:
                height = rect.height()
            else:
                height += rect.height()

            if i == n - 1:
                compartment.adjust(0, 0, 0, self._dy)

            compartments.append(compartment)
        return compartments

    def _positionTextItems(self) -> None:
        """Set text items' positions inside the corresponding compartments"""
        n = len(self._texts)
        for i in range(n):
            item: TextItem = self._text_items[i]
            compartment: QRectF = self._compartments[i]
            x = compartment.x() + self.padding
            if i == 0:
                # center first text item
                x += (compartment.width() - item.boundingRect().width()) / 2
            y = compartment.y() + self.padding
            item.setPos(x, y)

    def _getMaxHeight(self) -> float:
        """Return the total height of all compartments"""
        n = len(self._texts)
        height = 2.0 * self.padding if n == 0 else \
            sum(compartment.height() for compartment in self._compartments)
        return height

    def _recalculate(self):
        self.prepareGeometryChange()

        self._texts = re.split('\n--\n', self._text)

        self._deleteTextItems()
        self._text_items = self._createTextItems()
        width = self._getMaxWidth()
        self._compartments = self._createCompartments(width)
        self._positionTextItems()
        height = self._getMaxHeight()

        self._bounding_rect = QRectF(0, 0, width, height)

        self.update()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setPen(element_pen)
        painter.setBrush(element_brush)
        for compartment in self._compartments:
            painter.drawRect(compartment)

        if self.isSelected():
            painter.setPen(highlight_pen)
            painter.setBrush(highlight_brush)

            br = QPainterPath()
            br.addRect(self._bounding_rect)
            painter.fillPath(br, highlight_brush)

            painter.drawPath(self.shape())
