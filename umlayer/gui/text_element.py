from PySide6.QtCore import *
from PySide6.QtWidgets import *

from . import *


class TextElement(QGraphicsItem, BaseElement):
    def __init__(self, text, center: bool = False, parent=None) -> None:
        super().__init__(parent)
        super(BaseElement, self).__init__()
        self._abilities = set([Abilities.EDITABLE_TEXT])

        # serializable data
        self._text = text
        self._center = center
        # end of serializable data

        self._text_item = TextItem(text, parent=self)
        self._recalculate()

    def text(self):
        return self._text_item.text()

    def setText(self, text: str):
        self._text_item.setText(text)
        self._recalculate()

    def setCenter(self, center: bool):
        self._center = center
        self._recalculate()

    def _recalculate(self):
        self.prepareGeometryChange()
        self._bounding_rect = self._text_item.boundingRect()
        self.update()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        if option.state & QStyle.State_Selected:
            painter.setPen(highlight_pen)
            painter.setBrush(highlight_brush)

            br = QPainterPath()
            br.addRect(self._bounding_rect)
            painter.fillPath(br, highlight_brush)

            painter.drawPath(self.shape())
