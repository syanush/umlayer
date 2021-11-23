from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class NoteElement(QAbstractGraphicsShapeItem, BaseElement):
    def __init__(self, text: str = None, center=False, dx: float = 0, dy: float = 0, parent=None) -> None:
        super().__init__(parent)
        super(BaseElement, self).__init__()
        self._abilities = set([Abilities.EDITABLE_TEXT])

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # serializable data
        self._text = text
        self._center = center
        self._dx = dx  # must be non-negative
        self._dy = dy
        # end of serializable data

        self._text_item = TextItem(center=center, parent=self)
        self._recalculate()

    def text(self):
        return self._text

    def setText(self, text):
        self._text = text
        self._recalculate()

    def toDto(self):
        dto = super().toDto()
        dto['text'] = self.text()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setText(dto['text'])

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        return self._shape_path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Settings.element_pen)
        painter.setBrush(Settings.element_brush)
        painter.drawPath(self._border_path)

        if self.isSelected():
            painter.setPen(Settings.highlight_pen)
            painter.setBrush(Settings.highlight_brush)

            path = QPainterPath()
            path.addRect(self._bounding_rect)
            painter.fillPath(path, Settings.highlight_brush)

            painter.drawPath(self.shape())

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if self.scene() and \
                change == QGraphicsItem.ItemPositionChange and \
                QApplication.mouseButtons() == Qt.LeftButton:
            return QPointF(gui_utils.snap(value.x()), gui_utils.snap(value.y()))
        return super().itemChange(change, value)

    def _recalculate(self):
        self.prepareGeometryChange()
        text = self._text or ''
        self._text_item.setText(text)
        self._text_item.setPos(Settings.ELEMENT_PADDING, Settings.ELEMENT_PADDING)
        br = self._text_item.boundingRect()
        width = 2 * Settings.ELEMENT_PADDING + br.width() + self._dx + Settings.NOTE_DELTA
        height = 2 * Settings.ELEMENT_PADDING + br.height() + self._dy
        width = snap_up(width)
        height = snap_up(height)
        self._bounding_rect = QRectF(0, 0, width, height)

        br = self._bounding_rect
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

        self.update()
