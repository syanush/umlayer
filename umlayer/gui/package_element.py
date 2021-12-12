from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QStyleOptionGraphicsItem,
)

from . import gui_utils, Abilities, Settings, TextItem, ResizableElement


class PackageElement(ResizableElement):
    def __init__(
        self, text: str = None, dx: float = 0, dy: float = 0, parent=None
    ) -> None:
        super().__init__(dx=dx, dy=dy, parent=parent)
        self._abilities = {Abilities.EDITABLE_TEXT}

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # serializable data
        self._text = text or ""
        # end of serializable data

        self._text_item1 = TextItem(parent=self)
        self._text_item2 = TextItem(parent=self)
        self.recalculate()

    def text(self):
        return self._text

    def setText(self, text: str):
        if self._text != text:
            self._text = text
            self.recalculate()
            self.notify()

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
        return self._rect.adjusted(-extra, -extra, extra, extra)

    def shape(self) -> QPainterPath:
        return self._shape_path

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None
    ) -> None:
        self._text_item1.setColor(self.textColor())
        self._text_item2.setColor(self.textColor())

        pen = (
            Settings.ELEMENT_SELECTED_PEN
            if self.isSelected()
            else Settings.ELEMENT_NORMAL_PEN
        )
        painter.setPen(pen)
        painter.drawRect(self._rect1)
        painter.drawRect(self._rect2)

        if self.isSelected():
            shape_pen = Settings.ELEMENT_SHAPE_SELECTED_PEN
            painter.setPen(shape_pen)
            painter.drawPath(self.shape())

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        self.positionNotify(change)
        if (
            change == QGraphicsItem.ItemPositionChange
            and QApplication.mouseButtons() == Qt.LeftButton
        ):
            return QPointF(gui_utils.snap(value.x()), gui_utils.snap(value.y()))
        return super().itemChange(change, value)

    def recalculate(self):
        self.notify()
        self.prepareGeometryChange()

        self._text = self._text or ""
        self._text1, self._text2 = gui_utils.split_to_two_sections(self._text)

        self._text_item1.setText(self._text1)
        self._text_item2.setText(self._text2)
        self._text_item1.setPos(Settings.ELEMENT_PADDING, Settings.ELEMENT_PADDING)
        br1 = self._text_item1.boundingRect()
        width1 = br1.width() + 2 * Settings.ELEMENT_PADDING
        height1 = br1.height() + 2 * Settings.ELEMENT_PADDING
        if not self._text_item1.text():
            height1 = Settings.PACKAGE_EMPTY_HEIGHT1

        width1 = gui_utils.snap_up(width1)
        height1 = gui_utils.snap_up(height1)

        self._size1 = QPointF(width1, height1)
        self._text_item2.setPos(
            Settings.ELEMENT_PADDING, Settings.ELEMENT_PADDING + height1
        )
        br2 = self._text_item2.boundingRect()
        width2 = (
            max(
                width1 + Settings.PACKAGE_DELTA_WIDTH1,
                br2.width() + 2 * Settings.ELEMENT_PADDING,
            )
            + self.deltaX()
        )
        height2 = br2.height() + 2 * Settings.ELEMENT_PADDING + self.deltaY()
        width2 = gui_utils.snap_up(width2)
        height2 = gui_utils.snap_up(height2)

        self._size2 = QPointF(width2, height2)
        width = max(width1, width2)
        height = height1 + height2
        self._rect = QRectF(0, 0, width, height)
        self._rect1 = QRectF(0, 0, width1, height1)
        self._rect2 = QRectF(0, height1, width2, height2)

        x1 = self._size1.x()
        y1 = self._size1.y()
        x2 = self._size2.x()
        y2 = self._size2.y()
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(0, y1 + y2)
        path.lineTo(x2, y1 + y2)
        path.lineTo(x2, y1)
        path.lineTo(x1, y1)
        path.lineTo(x1, 0)
        path.lineTo(0, 0)
        self._shape_path = path

        self.updateHandlePositions()
