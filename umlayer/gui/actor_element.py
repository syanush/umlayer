from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *
from .. import model


class ActorElement(QGraphicsItemGroup, BaseElement):
    actor_width = 30
    actor_height = 65

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        super(BaseElement, self).__init__()
        self._abilities = set([Abilities.EDITABLE_TEXT])
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # serializable data
        self._text = text
        # end of serializable data

        self._text_item = TextItem(self._text, center=True, parent=self)

        self.items = (
            QGraphicsEllipseItem(5, 0, 20, 20, self),  # head
            QGraphicsLineItem(15, 20, 15, 45, self),  # vertical line
            QGraphicsLineItem(0, 25, 30, 25, self),  # horizontal line
            QGraphicsLineItem(15, 45, 0, 65, self),  # left leg
            QGraphicsLineItem(15, 45, 30, 65, self),  # right leg
        )

        self._recalculate()

    def text(self):
        return self._text_item.text()

    def setText(self, text: str):
        self._text = text
        self._recalculate()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        is_selected = option.state & QStyle.State_Selected
        pen = Settings.highlight_pen if is_selected else Settings.ACTOR_ELEMENT_PEN
        painter.setPen(pen)
        painter.drawPath(self.shape())

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if self.scene() and \
                change == QGraphicsItem.ItemPositionChange and \
                QApplication.mouseButtons() == Qt.LeftButton:
            return QPointF(gui_utils.snap(value.x()), gui_utils.snap(value.y()))
        return super().itemChange(change, value)

    def getDataAsDto(self):
        self.flags()
        return model.ActorElementModel(x=self.pos().x(), y=self.pos().y())

    def setDataFromDto(self, dto: model.ActorElementModel):
        self.setPos(QPointF(dto.x, dto.y))

    def _recalculate(self):
        self.prepareGeometryChange()

        self._text_item.setText(self._text or '')

        br = self._text_item.boundingRect()
        text_width = br.width()

        text_x = 1 + (self.actor_width - text_width) / 2
        text_y = self.actor_height + Settings.ELEMENT_PADDING
        self._text_item.setPos(text_x, text_y)

        self._bounding_rect = QRectF(0, 0, self.actor_width, self.actor_height)

        self.update()
