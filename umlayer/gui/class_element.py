from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import (
    QApplication, QAbstractGraphicsShapeItem, QGraphicsItem,
    QStyleOptionGraphicsItem)

from . import gui_utils, Abilities, BaseElement, Settings, TextItem


class ClassElement(QAbstractGraphicsShapeItem, BaseElement):
    def __init__(self, text: str = '', dx: float = 0, dy: float = 0, parent=None) -> None:
        super().__init__(parent)
        BaseElement.__init__(self)
        self._abilities = {Abilities.EDITABLE_TEXT}

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

    def setText(self, text: str):
        if self._text != text:
            self._text = text
            self._recalculate()

    def deltaX(self):
        return self._dx

    def setDeltaX(self, dx):
        if self._dx != dx:
            self._dx = dx
            self._recalculate()

    def deltaY(self):
        return self._dy

    def setDeltaY(self, dy):
        if self._dy != dy:
            self._dy = dy
            self._recalculate()

    def toDto(self):
        dto = super().toDto()
        dto['text'] = self.text()
        dto['dx'] = self.deltaX()
        dto['dy'] = self.deltaY()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setText(dto['text'])
        self.setDeltaX(dto['dx'])
        self.setDeltaY(dto['dy'])

    def boundingRect(self) -> QRectF:
        extra = max(Settings.ELEMENT_PEN_SIZE, Settings.ELEMENT_SHAPE_SIZE) / 2
        return self._rect.adjusted(-extra, -extra, extra, extra)

    def shape(self) -> QPainterPath:
        return self._shape_path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        for item in self._text_items:
            item.setColor(self.textColor())

        pen = Settings.ELEMENT_SELECTED_PEN if self.isSelected() else Settings.ELEMENT_NORMAL_PEN
        painter.setPen(pen)
        for compartment in self._compartments:
            painter.drawRect(compartment)

        if self.isSelected():
            shape_pen = Settings.ELEMENT_SHAPE_SELECTED_PEN
            painter.setPen(shape_pen)
            painter.drawPath(self.shape())

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        self.positionNotify(change)
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
        width = gui_utils.snap_up(width)

        self._compartments = self._createCompartments(width)
        self._positionTextItems()
        height = self._getMaxHeight()

        self._rect = QRectF(0, 0, width, height)
        path = QPainterPath()
        path.addRect(self._rect)
        self._shape_path = path

        self.update()
        self.notify()

    def _get_rect(self, item: TextItem) -> QRectF:
        br = item.boundingRect()
        width = br.width() + 2 * Settings.ELEMENT_PADDING
        height = br.height() + 2 * Settings.ELEMENT_PADDING
        rect = QRectF(0, 0, width, height)
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
        width = 2 * Settings.ELEMENT_PADDING if n == 0 else \
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
            comp_height = rect.height()
            if item.text() == "":
                comp_height = Settings.CLASS_MIN_COMPARTMENT_HEIGHT
            compartment = QRectF(0, height, width, comp_height)

            if i == 0:
                height = compartment.height()
            else:
                height += compartment.height()

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
            height1 = gui_utils.snap_up(height)
            self._compartments[-1].adjust(0, 0, 0, height1 - height)
            height = height1
        return height
