from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *
from . import gui_utils


class ClassElement(QAbstractGraphicsShapeItem, BaseElement):
    def __init__(self, text: str = '', dx: float = 0, dy: float = 0, parent=None) -> None:
        super().__init__(parent)
        super(BaseElement, self).__init__()
        self._abilities = set([Abilities.EDITABLE_TEXT])

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

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

    def toDto(self):
        dto = super().toDto()
        dto['text'] = self.text()
        dto['dx'] = self._dx
        dto['dy'] = self._dy
        self._recalculate()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setText(dto['text'])
        self._dx = dto['dx']
        self._dy = dto['dy']

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setPen(Settings.element_pen)
        painter.setBrush(Settings.element_brush)
        for compartment in self._compartments:
            painter.drawRect(compartment)

        if self.isSelected():
            painter.setPen(Settings.highlight_pen)
            painter.setBrush(Settings.highlight_brush)

            br = QPainterPath()
            br.addRect(self._bounding_rect)
            painter.fillPath(br, Settings.highlight_brush)

            painter.drawPath(self.shape())

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if self.scene() and \
                change == QGraphicsItem.ItemPositionChange and \
                QApplication.mouseButtons() == Qt.LeftButton:
            return QPointF(gui_utils.snap(value.x()), gui_utils.snap(value.y()))

        return super().itemChange(change, value)

    def _recalculate(self):
        self.prepareGeometryChange()

        self._texts = gui_utils.split_to_sections(self._text)

        self._deleteTextItems()
        self._text_items = self._createTextItems()
        width = self._getMaxWidth()
        width = snap_up(width)

        self._compartments = self._createCompartments(width)
        self._positionTextItems()
        height = self._getMaxHeight()

        self._bounding_rect = QRectF(0, 0, width, height)

        self.update()

    def _get_rect(self, item: TextItem) -> QRectF:
        br = item.boundingRect()
        width = br.width() + 2.0 * Settings.ELEMENT_PADDING
        height = br.height() + 2.0 * Settings.ELEMENT_PADDING
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
                x = compartment.x() + Settings.ELEMENT_PADDING
            y = compartment.y() + Settings.ELEMENT_PADDING
            item.setPos(x, y)

    def _getMaxHeight(self) -> float:
        """Return the total height of all compartments"""
        n = len(self._texts)
        height = 2.0 * Settings.ELEMENT_PADDING
        if n > 0:
            height = sum(compartment.height() for compartment in self._compartments)
            height1 = snap_up(height)
            self._compartments[-1].adjust(0, 0, 0, height1 - height)
            height = height1
        return height
