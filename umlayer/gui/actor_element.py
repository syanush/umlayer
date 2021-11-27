from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class ActorElement(QGraphicsItem, BaseElement):
    actor_width = 30
    actor_height = 65

    def __init__(self, text: str = '', parent=None):
        super().__init__(parent=parent)
        BaseElement.__init__(self)
        self._abilities = set([Abilities.EDITABLE_TEXT])

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # serializable data
        self._text = text or ''
        # end of serializable data

        self._text_item = TextItem(self._text, center=True, parent=self)

        self.items = (
            QGraphicsEllipseItem(5, 0, 20, 20, parent=self),  # head
            QGraphicsLineItem(15, 20, 15, 45, parent=self),  # vertical line
            QGraphicsLineItem(0, 25, 30, 25, parent=self),  # horizontal line
            QGraphicsLineItem(15, 45, 0, 65, parent=self),  # left leg
            QGraphicsLineItem(15, 45, 30, 65, parent=self),  # right leg
        )

        self._recalculate()

    def text(self):
        return self._text_item.text()

    def setText(self, text: str):
        if self._text != text:
            self._text = text
            self._recalculate()

    def rect(self) -> QRectF:
        return self._rect

    def boundingRect(self) -> QRectF:
        extra = max(Settings.ELEMENT_PEN_SIZE, Settings.ELEMENT_SHAPE_SIZE) / 2
        return self._rect.adjusted(-extra, -extra, extra, extra)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.rect())
        return path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        pen = Settings.ELEMENT_SELECTED_PEN if self.isSelected() else Settings.ELEMENT_NORMAL_PEN
        self._setElementPen(pen)

        text_pen = Settings.ELEMENT_TEXT_SELECTED_PEN if self.isSelected() else Settings.ELEMENT_TEXT_NORMAL_PEN
        self._text_item.setPen(text_pen)

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

    def toDto(self):
        dto = super().toDto()
        dto['text'] = self.text()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setText(dto['text'])

    def _recalculate(self):
        self.prepareGeometryChange()

        self._text_item.setText(self._text or '')

        br = self._text_item.boundingRect()
        text_width = br.width()

        text_x = 1 + (self.actor_width - text_width) / 2
        text_y = self.actor_height + Settings.ELEMENT_PADDING
        self._text_item.setPos(text_x, text_y)

        text_rect = QRectF(text_x, text_y, br.width(), br.height())
        actor_rect = QRectF(0, 0, self.actor_width, self.actor_height)
        self._rect = actor_rect.united(text_rect)

        self.update()
        self.notify()

    def _setElementPen(self, pen):
        for item in self.items:
            item.setPen(pen)
