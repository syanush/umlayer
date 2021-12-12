from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem

from . import gui_utils, Abilities, Settings, TextItem, ResizableElement


class EllipseElement(ResizableElement):
    def __init__(
        self, dx: float = 0, dy: float = 0, text: str = None, parent=None
    ) -> None:
        super().__init__(dx=dx, dy=dy, parent=parent)
        self._abilities = {Abilities.EDITABLE_TEXT}

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # serializable data
        self._text = text or ""
        # end of serializable data

        self._text_item = TextItem(center=True, parent=self)
        self.recalculate()

    def text(self):
        return self._text

    def setText(self, text: str):
        if self._text == text:
            return
        self._text = text
        self.recalculate()

    def rect(self) -> QRectF:
        return self._rect

    def toDto(self):
        dto = super().toDto()
        dto["text"] = self.text()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setText(dto["text"])

    def boundingRect(self) -> QRectF:
        extra = max(Settings.ELEMENT_PEN_SIZE, Settings.ELEMENT_SHAPE_SIZE) / 2
        return self.rect().adjusted(-extra, -extra, extra, extra)

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
        painter.drawEllipse(self.rect())

        if self.isSelected():
            shape_pen = Settings.ELEMENT_SHAPE_SELECTED_PEN
            painter.setPen(shape_pen)
            painter.drawPath(self.shape())

    def recalculate(self):
        self.notify()
        self.prepareGeometryChange()

        text = self._text or ""
        self._text_item.setText(text)
        br = self._text_item.boundingRect()

        width = gui_utils.snap_up(
            br.width() * Settings.ELLIPSE_SCALE_WIDTH + self.deltaX()
        )
        height = gui_utils.snap_up(
            br.height() * Settings.ELLIPSE_SCALE_HEIGHT + self.deltaY()
        )
        self._rect = QRectF(0, 0, width, height)

        x = (self.rect().width() - br.width()) / 2
        y = (self.rect().height() - br.height()) / 2
        self._text_item.setPos(x, y)

        path = QPainterPath()
        path.addEllipse(self.rect())
        self._shape_path = path

        self.updateHandlePositions()
