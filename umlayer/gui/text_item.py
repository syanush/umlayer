from PySide6.QtWidgets import (
    QGraphicsTextItem
)


class TextItem(QGraphicsTextItem):
    def __init__(self, text: str = None, center: bool = False, parent=None) -> None:
        super().__init__(parent)

        # serializable data
        self._text = text or ''
        self._center = center
        # end of serializable data

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

    def setColor(self, color):
        self.setDefaultTextColor(color)

    def _getHtml(self, text):
        alignment = 'center' if self.center() else 'left'
        return f"""
<div align="{alignment}"
style="
font-family: Segoe UI;
font-size: 15px;
white-space: pre;
">{text}</div>
"""

    def _recalculate(self):
        self.prepareGeometryChange()
        html = self._getHtml(self._text)
        # print(html)
        self.setHtml(html)
        self.adjustSize()
        self.update()
