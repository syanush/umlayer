from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class EllipseElement(QGraphicsItem, BaseElement):
    def __init__(self, width: int = 10, height: int = 10, text: str = None, parent=None) -> None:
        super().__init__(parent)
        BaseElement.__init__(self)
        self._abilities = {Abilities.EDITABLE_TEXT}

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

    def width(self):
        return self._width

    def setWidth(self, width):
        if self._width != width:
            self._width = width
            self._recalculate()

    def height(self):
        return self._height

    def setHeight(self, height):
        if self._height != height:
            self._height = height
            self._recalculate()

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
        extra = max(Settings.ELEMENT_PEN_SIZE, Settings.ELEMENT_SHAPE_SIZE) / 2
        return self._rect.adjusted(-extra, -extra, extra, extra)

    def shape(self) -> QPainterPath:
        return self._shape_path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        text_pen = Settings.ELEMENT_TEXT_SELECTED_PEN if self.isSelected() else Settings.ELEMENT_TEXT_NORMAL_PEN
        self._text_item.setPen(text_pen)

        pen = Settings.ELEMENT_SELECTED_PEN if self.isSelected() else Settings.ELEMENT_NORMAL_PEN
        painter.setPen(pen)
        painter.drawEllipse(0, 0, self._width, self._height)

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
        text = self._text or ''
        self._text_item.setText(text)
        br = self._text_item.boundingRect()
        x = (self._width - br.width()) / 2
        y = (self._height - br.height()) / 2
        self._text_item.setPos(x, y)
        self._rect = QRectF(0, 0, self._width, self._height)
        path = QPainterPath()
        path.addEllipse(self._rect)
        self._shape_path = path
        self.update()
        self.notify()
