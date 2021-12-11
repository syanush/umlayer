from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import (
    QStyleOptionGraphicsItem,
)

from . import (
    gui_utils,
    Abilities,
    Settings,
    TextItem,
    ResizableElement, ResizeHandleItem, Handler
)


class NoteElement(ResizableElement):
    def __init__(
        self, text: str = None, center=False, dx: float = 0, dy: float = 0, parent=None
    ) -> None:
        super().__init__(dx=dx, dy=dy, parent=parent)
        self._abilities = {Abilities.EDITABLE_TEXT}

        # serializable data
        self._text = text
        self._center = center
        # end of serializable data

        self._text_item = TextItem(center=center, parent=self)
        self.setLive(False)
        self.recalculate()

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        if self._text != text:
            self._text = text
            self.recalculate()

    def center(self) -> bool:
        return self._center

    def setCenter(self, center: bool) -> None:
        if self._center != center:
            self._center = center
            self.recalculate()

    def rect(self) -> QRectF:
        return self._rect

    def toDto(self) -> dict:
        dto = super().toDto()
        dto["text"] = self.text()
        dto["center"] = self.center()
        return dto

    def setFromDto(self, dto: dict) -> None:
        super().setFromDto(dto)
        self.setText(dto["text"])
        self.setCenter(dto["center"])

    def boundingRect(self) -> QRectF:
        extra = max(Settings.ELEMENT_PEN_SIZE, Settings.ELEMENT_SHAPE_SIZE) / 2
        return self._rect.adjusted(-extra, -extra, extra, extra)

    def shape(self) -> QPainterPath:
        return self._shape_path

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None
    ) -> None:
        self._text_item.setColor(self.textColor())

        pen = (
            Settings.ELEMENT_SELECTED_PEN
            if self.isSelected()
            else Settings.ELEMENT_NORMAL_PEN
        )
        painter.setPen(pen)
        painter.drawPath(self._border_path)

        if self.isSelected():
            shape_pen = Settings.ELEMENT_SHAPE_SELECTED_PEN
            painter.setPen(shape_pen)
            painter.drawPath(self.shape())

    def recalculate(self) -> None:
        self.notify()
        self.prepareGeometryChange()

        text = self._text or ""
        self._text_item.setText(text)
        self._text_item.setPos(Settings.ELEMENT_PADDING, Settings.ELEMENT_PADDING)
        br = self._text_item.boundingRect()
        width = (
            2 * Settings.ELEMENT_PADDING + br.width() + self._dx + Settings.NOTE_DELTA
        )
        height = 2 * Settings.ELEMENT_PADDING + br.height() + self._dy
        width = gui_utils.snap_up(width)
        height = gui_utils.snap_up(height)
        self._rect = QRectF(0, 0, width, height)

        br = self._rect
        x = br.width()
        y = br.height()
        path = QPainterPath()
        path.moveTo(x - Settings.NOTE_DELTA, 0)
        path.lineTo(0, 0)
        path.lineTo(0, y)
        path.lineTo(x, y)
        path.lineTo(x, Settings.NOTE_DELTA)
        path.lineTo(x - Settings.NOTE_DELTA, 0)
        self._shape_path = path

        path = QPainterPath()
        path.moveTo(x - Settings.NOTE_DELTA, 0)
        path.lineTo(0, 0)
        path.lineTo(0, y)
        path.lineTo(x, y)
        path.lineTo(x, Settings.NOTE_DELTA)
        path.lineTo(x - Settings.NOTE_DELTA, Settings.NOTE_DELTA)
        path.lineTo(x - Settings.NOTE_DELTA, 0)
        path.lineTo(x, Settings.NOTE_DELTA)
        self._border_path = path

        self.updateHandlePositions()
