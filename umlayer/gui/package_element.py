from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class PackageElement(QAbstractGraphicsShapeItem, BaseElement):
    def __init__(self, text: str = None, dx: float = 0, dy: float = 0, parent=None) -> None:
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

        self._text_item1 = TextItem(parent=self)
        self._text_item2 = TextItem(parent=self)
        self._recalculate()

    def text(self):
        return self._text

    def setText(self, text: str):
        if self._text != text:
            self._text = text
            self._recalculate()
            self.notify()

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
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        return self._shape_path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Settings.element_pen)
        painter.setBrush(Settings.element_brush)
        painter.drawRect(self._rect1)
        painter.drawRect(self._rect2)

        if self.isSelected():
            painter.setPen(Settings.highlight_pen)
            painter.setBrush(Settings.highlight_brush)

            # br = QPainterPath()
            # br.addRect(self._bounding_rect)
            # painter.fillPath(br, highlight_brush)

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

        # TODO: improve parsing
        self._text = self._text or ''
        self._text1, self._text2 = gui_utils.split_to_two_sections(self._text)

        self._text_item1.setText(self._text1)
        self._text_item2.setText(self._text2)
        self._text_item1.setPos(Settings.ELEMENT_PADDING, Settings.ELEMENT_PADDING)
        br1 = self._text_item1.boundingRect()
        size1_x = br1.width() + 2 * Settings.ELEMENT_PADDING
        size1_y = br1.height() + 2 * Settings.ELEMENT_PADDING
        size1_x = snap_up(size1_x)
        size1_y = snap_up(size1_y)

        self._size1 = QPointF(size1_x, size1_y)
        self._text_item2.setPos(Settings.ELEMENT_PADDING, Settings.ELEMENT_PADDING + size1_y)
        br2 = self._text_item2.boundingRect()
        size2_x = max(br2.width() + 2 * Settings.ELEMENT_PADDING + self._dx, size1_x + Settings.HANDLE_MIN2 + self._dx)
        size2_y = br2.height() + 2 * Settings.ELEMENT_PADDING + self._dy
        size2_x = snap_up(size2_x)
        size2_y = snap_up(size2_y)

        self._size2 = QPointF(size2_x, size2_y)
        width = max(size1_x, size2_x)
        height = size1_y + size2_y
        self._bounding_rect = QRectF(0, 0, width, height)
        self._rect1 = QRectF(0, 0, size1_x, size1_y)
        self._rect2 = QRectF(0, size1_y, size2_x, size2_y)

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
        self._shape_path = path

        self.update()
        self.notify()
