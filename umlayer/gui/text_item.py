from PySide6.QtCore import *
from PySide6.QtWidgets import *

from . import *


class TextItem(QGraphicsItem):
    def __init__(self, text, center: bool = False, parent=None) -> None:
        super().__init__(parent)

        # serializable data
        self._text = text
        self._center = center
        # end of serializable data

        self._recalculate()

    def text(self):
        return self._text

    def setText(self, text: str):
        self._text = text
        self._recalculate()

    def setCenter(self, center: bool):
        self._center = center
        self._recalculate()

    def text_size(self, text):
        """ Returns the size (dx,dy) of the specified text string (using the
            current control font).
        """
        # TODO: possible bug when using dynamic fonts
        rect = QFontMetrics(diagram_font).boundingRect(text)
        return rect.width(), rect.height()

    def _recalculate(self):
        self.prepareGeometryChange()
        self._lines = [' ' if line == '' else line for line in self._text.split('\n')]
        width = 0.0
        height = 0.0
        n = len(self._lines)
        if n > 0:
            txt_sizes = [self.text_size(line) for line in self._lines]
            width = max(w for w, h in txt_sizes)
            height = sum(h for w, h in txt_sizes)

        self._bounding_rect = QRectF(0, int(0), width, height)
        self.update()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setFont(diagram_font)
        n = len(self._lines)
        if n > 0:
            line_height = self._bounding_rect.height() / n
            text_width = self._bounding_rect.width()

            for i in range(n):
                line = self._lines[i]
                br_width, br_height = self.text_size(line)
                if self._center:
                    x = (text_width - br_width) / 2
                else:
                    x = 0
                y = line_height * i
                painter.drawText(QRect(x, y, br_width, br_height), line)
