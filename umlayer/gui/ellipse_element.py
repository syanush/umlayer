from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class EllipseElement(QGraphicsItem, BaseElement):
    def __init__(self, width: int = 10, height: int = 10, text: str = None, parent=None) -> None:
        super().__init__(parent)
        BaseElement.__init__(self)
        self._abilities = set([Abilities.EDITABLE_TEXT])

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # serializable data
        self._text = text or ''
        self._width = max(width, 10)
        self._height = max(height, 10)  # must be >= 10
        # end of serializable data

        self._text_item = TextItem(center=True, parent=self)
        self._recalculate()

    def text(self):
        return self._text

    def setText(self, text: str):
        if self._text != text:
            self._text = text
            self._recalculate()
            self.notify()

    def width(self):
        return self._width

    def setWidth(self, width):
        if self._width != width:
            self._width = width
            self._recalculate()
            self.notify()

    def height(self):
        return self._height

    def setHeight(self, height):
        if self._height != height:
            self._height = height
            self._recalculate()
            self.notify()

    def toDto(self):
        dto = super().toDto()
        dto['text'] = self.text()
        dto['width'] = self.width()
        dto['height'] = self.height()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setText(dto['text'])
        self.setWidth(dto['width'])
        self.setHeight(dto['height'])

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        return self._shape_path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(Settings.element_pen)
        painter.setBrush(Settings.element_brush)
        painter.drawEllipse(0, 0, self._width, self._height)

        if self.isSelected():
            painter.setPen(Settings.highlight_pen)
            painter.setBrush(Settings.highlight_brush)
            br = QPainterPath()
            br.addRect(self._bounding_rect)
            painter.fillPath(br, Settings.highlight_brush)
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
        text = self._text or ''
        self._text_item.setText(text)
        br = self._text_item.boundingRect()
        x = (self._width - br.width()) / 2
        y = (self._height - br.height()) / 2
        self._text_item.setPos(x, y)
        self._bounding_rect = QRectF(0, 0, self._width, self._height)
        path = QPainterPath()
        path.addEllipse(self._bounding_rect)
        self._shape_path = path
        self.update()
