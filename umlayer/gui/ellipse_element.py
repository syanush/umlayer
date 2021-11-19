from PySide6.QtCore import *
from PySide6.QtWidgets import *

from . import *


class EllipseElement(QGraphicsItem, BaseElement):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        super(BaseElement, self).__init__()
        self._abilities = set([Abilities.EDITABLE_TEXT])

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

        # serializable data
        self._text = 'Use case 1'
        self._width = 150  # must be >= 10
        self._height = 50  # must be >= 10
        # end of serializable data

        self._text_lines = TextItem(self._text, center=True, parent=self)

        self._recalculate()

    def text(self):
        return self._text_lines.text()

    def setText(self, text):
        self._text_lines.setText(text)
        self._recalculate()

    def _recalculate(self):
        self.prepareGeometryChange()
        br = self._text_lines.boundingRect()
        x = (self._width - br.width()) / 2
        y = (self._height - br.height()) / 2
        self._text_lines.setPos(x, y)
        self._bounding_rect = QRectF(0, 0, self._width, self._height)
        self.update()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addEllipse(self._bounding_rect)
        return path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(element_pen)
        painter.setBrush(element_brush)
        painter.drawEllipse(0, 0, self._width, self._height)

        if option.state & QStyle.State_Selected:
            painter.setPen(highlight_pen)
            painter.setBrush(highlight_brush)
            br = QPainterPath()
            br.addRect(self._bounding_rect)
            painter.fillPath(br, highlight_brush)
            painter.drawPath(self.shape())
