from PySide6.QtCore import *
from PySide6.QtWidgets import *

from . import *


class TextItem(QGraphicsItem):
    correction_factor = 0.925

    def __init__(self, text: str = None, center: bool = False, parent=None) -> None:
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

    def get_painting_device(self):
        pd = None
        scene = self.scene()
        if scene is not None:
            views = self.scene().views()
            if len(views) > 0:
                pd = views[0]
        return pd

    def text_size(self, text):
        """
        Returns the size (dx,dy) of the specified text string (using the
        current control font).

        TODO: possible bug when the font changes at runtime

        The width of the bounding box is mysteriously larger than the width of the displayed text.
        Two ugly hacks try to address this problem.
        Hack #1: Use painting device in the constructor of QFontMetrics
        and improve bounding rect evaluation
        https://stackoverflow.com/questions/27336001/qfontmetrics-returns-inaccurate-results

        Hack #2: Apply empirical correction factor. It is specific for the improved rect.
        Please check if it is different for various fonts and platforms.
        """

        pd = self.get_painting_device()
        fm = QFontMetrics(element_font, pd=pd)
        rect = fm.boundingRect(text)
        improved_rect = fm.boundingRect(rect, 0, text)
        width = improved_rect.width()
        height = improved_rect.height()
        # width *= self.correction_factor
        return width, height

    def _recalculate(self):
        self.prepareGeometryChange()

        text = self._text or ''
        self._lines = [' ' if line == '' else line for line in text.split('\n')]
        width = 0.0
        height = 0.0
        n = len(self._lines)
        if n > 0:
            txt_sizes = [self.text_size(line) for line in self._lines]
            width = max(w for w, h in txt_sizes)
            height = sum(h for w, h in txt_sizes)

        self._bounding_rect = QRectF(0, 0, width, height)
        self.update()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setFont(element_font)
        painter.setPen(element_pen)
        painter.setBrush(element_brush)
        # painter.drawRect(self._bounding_rect)  # for debugging
        n = len(self._lines)
        if n > 0:
            avg_line_height = self._bounding_rect.height() / n
            text_width = self._bounding_rect.width()

            for i in range(n):
                line = self._lines[i]
                line_width, line_height = self.text_size(line)
                if self._center:
                    x = (text_width - line_width) / 2
                else:
                    x = 0
                y = avg_line_height * i
                line_rect = QRect(x, y, line_width, line_height)
                painter.drawText(line_rect, line)
