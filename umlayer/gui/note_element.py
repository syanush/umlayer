from PySide6.QtCore import *
from PySide6.QtWidgets import *

from . import *


class NoteElement(QAbstractGraphicsShapeItem, BaseElement):
    padding = 5
    delta = 15

    def __init__(self, text: str, center=False, dx: float = 50, dy: float = 30, parent=None) -> None:
        super().__init__(parent)
        super(BaseElement, self).__init__()
        self._abilities = set([Abilities.EDITABLE_TEXT])

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

        # serializable data
        self._text = text
        self._center = center
        self._dx = dx  # must be non-negative
        self._dy = dy
        # end of serializable data

        self._text_lines = TextItem(self._text, center=center, parent=self)
        self._recalculate()

    def text(self):
        return self._text_lines.text()

    def setText(self, text):
        self._text_lines.setText(text)
        self._recalculate()

    def _recalculate(self):
        self.prepareGeometryChange()
        br = self._text_lines.boundingRect()
        width = 2 * self.padding + br.width() + self._dx + self.delta
        height = 2 * self.padding + br.height() + self._dy
        self._bounding_rect = QRectF(0, 0, width, height)
        self._text_lines.setPos(self.padding, self.padding)
        self.update()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        br = self._bounding_rect
        x = br.width()
        y = br.height()
        path = QPainterPath()
        path.moveTo(x - self.delta, 0)
        path.lineTo(0, 0)
        path.lineTo(0, y)
        path.lineTo(x, y)
        path.lineTo(x, self.delta)
        path.lineTo(x - self.delta, 0)
        return path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(item_pen)
        painter.setBrush(item_brush)

        br = self._bounding_rect
        x = br.width()
        y = br.height()
        path = QPainterPath()
        path.moveTo(x - self.delta, 0)
        path.lineTo(0, 0)
        path.lineTo(0, y)
        path.lineTo(x, y)
        path.lineTo(x, self.delta)
        path.lineTo(x - self.delta, self.delta)
        path.lineTo(x - self.delta, 0)
        path.lineTo(x, self.delta)
        painter.drawPath(path)

        if option.state & QStyle.State_Selected:
            painter.setPen(highlight_pen)
            painter.setBrush(highlight_brush)

            path = QPainterPath()
            path.addRect(self._bounding_rect)
            painter.fillPath(path, highlight_brush)

            painter.drawPath(self.shape())
