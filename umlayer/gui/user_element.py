"""User element of the Use Case diagram"""

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *
from .. import model


class UserElement(QGraphicsItemGroup):
    padding = 5
    _bounding_rect = QRectF(0, 0, 30, 65)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        # serializable data
        self._text = 'Actor'
        # end of serializable data
        
        self.items = (
            QGraphicsEllipseItem(5, 0, 20, 20, self),  # head
            QGraphicsLineItem(15, 20, 15, 45, self),  # vertical line
            QGraphicsLineItem(0, 25, 30, 25, self),  # horizontal line
            QGraphicsLineItem(15, 45, 0, 65, self),  # left leg
            QGraphicsLineItem(15, 45, 30, 65, self),  # right leg
        )

        for item in self.items:
            self.addToGroup(item)

        self._text_item = QGraphicsTextItem(self)
        self._text_item.setFont(diagram_font)
        self._text_item.setDefaultTextColor(Qt.black)

        self._recalculate()

    def _recalculate(self):
        actor_height = 65
        self._text_item.setPlainText(self._text)
        text_width = self._text_item.boundingRect().width()
        # text_height = self._text_item.boundingRect().height()
        text_x = 15 - text_width / 2 + 1
        text_y = actor_height
        self._text_item.setPos(text_x, text_y)
        # self._selection_rect = QRectF(min(text_x, 0), 0,  max(30, text_width), text_y + text_height)

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        if option.state & QStyle.State_Selected:
            # painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(highlight_pen)
            painter.setBrush(highlight_brush)

            # br = QPainterPath()
            # br.addRect(self._selection_rect)
            # painter.fillPath(br, highlight_brush)

            painter.drawPath(self.shape())

    def shape(self) -> QPainterPath:
        br = self.boundingRect()
        path = QPainterPath()
        path.addRect(br)
        return path

        # path.moveTo(0, 65)
        # path.lineTo(0, 0)
        # path.lineTo(30, 0)
        # path.lineTo(30, 65)
        # path.lineTo(15 + w / 2, 65)
        # path.lineTo(15 + w / 2, 65 + h)
        # path.lineTo(15 - w / 2, 65 + h)
        # path.lineTo(15 - w / 2, 65)
        # path.lineTo(0, 65)
        #
        # return path

    def getDataAsDto(self):
        self.flags()
        return model.UserElementModel(x=self.pos().x(), y=self.pos().y())

    def setDataFromDto(self, dto: model.UserElementModel):
        self.setPos(QPointF(dto.x, dto.y))
