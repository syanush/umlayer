from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class TextElement(QGraphicsItem, BaseElement):
    def __init__(self, text: str = None, center: bool = False, parent=None) -> None:
        super().__init__(parent)
        BaseElement.__init__(self)
        self._abilities = set([Abilities.EDITABLE_TEXT])

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # serializable data
        self._text = text or ''
        self._center = center
        # end of serializable data

        self._text_item = TextItem(parent=self)
        self._recalculate()

    def text(self):
        return self._text

    def setText(self, text: str):
        if self._text != text:
            self._text = text
            self._recalculate()

    def center(self):
        return self._center

    def setCenter(self, center: bool):
        if self._center != center:
            self._center = center
            self._recalculate()

    def toDto(self):
        dto = super().toDto()
        dto['text'] = self._text
        dto['center'] = self._center
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setText(dto['text'])
        self.setCenter(dto['center'])

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
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
        self._text_item.setCenter(self._center)
        self._bounding_rect = self._text_item.boundingRect()
        self.update()
        self.notify()
