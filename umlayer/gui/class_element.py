from PySide6.QtCore import *
from PySide6.QtWidgets import *

from . import *


class ClassElement(QAbstractGraphicsShapeItem, BaseElement):
    padding = 5

    def __init__(self, text: str = '', dx: float = 0, dy: float = 0, parent=None) -> None:
        super().__init__(parent)
        super(BaseElement, self).__init__()
        self._abilities = set([Abilities.EDITABLE_TEXT])

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

        # serializable data
        self._text = text or ''
        self._dx = dx  # must be non-negative
        self._dy = dy
        # end of serializable data

        self._text_items = []
        self._recalculate()

    def text(self):
        return self._text

    def setText(self, text):
        self._text = text
        self._recalculate()

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

    def _recalculate(self):
        self.prepareGeometryChange()

        self._texts = ClassElement._parseText(self._text)

        self._deleteTextItems()
        self._text_items = self._createTextItems()
        width = self._getMaxWidth()
        self._compartments = self._createCompartments(width)
        self._positionTextItems()
        height = self._getMaxHeight()

        self._bounding_rect = QRectF(0, 0, width, height)

        self.update()

    @staticmethod
    def _parseText(text) -> list[str]:
        """"Return the list of text sections.

        The separator of the sections is '--\n' line in the original text
        """
        lines = text.split('\n')
        sections = []
        section_lines = []
        for line in lines:
            if line == '--':
                section = '\n'.join(section_lines)
                sections.append(section)
                section_lines.clear()
            else:
                section_lines.append(line)
        section = '\n'.join(section_lines)
        sections.append(section)
        section_lines.clear()
        return sections

        # print(ClassElement._parseText('--')) # 2
        # print(ClassElement._parseText('--\n')) # 2
        # print(ClassElement._parseText('--\n--')) # 3
        # print(ClassElement._parseText('--\n--\n')) # 3

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
            if i == 0:
                # Center first text item. The padding is already included in compartment.width().
                x = compartment.x() + (compartment.width() - item.boundingRect().width()) / 2
            else:
                # Left-align other items
                x = compartment.x() + self.padding
            y = compartment.y() + self.padding
            item.setPos(x, y)

    def _getMaxHeight(self) -> float:
        """Return the total height of all compartments"""
        n = len(self._texts)
        height = 2.0 * self.padding if n == 0 else \
            sum(compartment.height() for compartment in self._compartments)
        return height
