from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import QApplication, QGraphicsItem, QStyleOptionGraphicsItem

from . import gui_utils, Abilities, BaseElement, Settings, TextItem


class TextElement(BaseElement):
    def __init__(self, text: str = None, center: bool = False, parent=None) -> None:
        super().__init__(parent=parent)
        self._abilities = {Abilities.EDITABLE_TEXT}

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # serializable data
        self._text = text or ""
        self._center = center
        # end of serializable data

        self._text_item = TextItem(parent=self)
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

    def toDto(self):
        dto = super().toDto()
        dto["text"] = self._text
        dto["center"] = self._center
        return dto

    def setFromDto(self, dto: dict):
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

        if self.isSelected():
            painter.setPen(Settings.ELEMENT_SHAPE_SELECTED_PEN)
            painter.drawPath(self.shape())

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        self.positionNotify(change)
        if (
            change == QGraphicsItem.ItemPositionChange
            and QApplication.mouseButtons() == Qt.LeftButton
        ):
            return QPointF(gui_utils.snap(value.x()), gui_utils.snap(value.y()))
        return super().itemChange(change, value)

    def _recalculate(self):
        self.prepareGeometryChange()
        text = self._text or ""
        self._text_item.setText(text)
        self._text_item.setCenter(self.center())
        self._rect = self._text_item.boundingRect()
        path = QPainterPath()
        path.addRect(self._rect)
        self._shape_path = path
        self.update()
        self.notify()
