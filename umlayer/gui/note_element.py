from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QStyleOptionGraphicsItem,
)

from . import (
    gui_utils,
    Abilities,
    BaseElement,
    Settings,
    Handler,
    TextItem,
    ResizeHandleItem,
)


class NoteElement(BaseElement):
    def __init__(
        self, text: str = None, center=False, dx: float = 0, dy: float = 0, parent=None
    ) -> None:
        super().__init__(parent=parent)
        self._abilities = {Abilities.EDITABLE_TEXT}

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # serializable data
        self._text = text
        self._center = center
        self._dx = dx  # must be non-negative
        self._dy = dy
        # end of serializable data

        self._handler = Handler(item=self)
        for i in range(1, 4 + 1):
            self._handler.handle[i] = ResizeHandleItem(
                size=Settings.RESIZE_HANDLE_SIZE, item=self
            )

        self._handler.on_zvalue_change()

        for handle in self._handler.handle.values():
            handle.selection_changed_signal.connect(self._handle_selection_changed)

        self.setLive(False)

        self._text_item = TextItem(center=center, parent=self)
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

    def deltaX(self):
        return self._dx

    def setDeltaX(self, dx):
        if self._dx != dx:
            self._dx = dx
            self._recalculate()

    def deltaY(self):
        return self._dy

    def setDeltaY(self, dy):
        if self._dy != dy:
            self._dy = dy
            self._recalculate()

    def toDto(self):
        dto = super().toDto()
        dto["text"] = self.text()
        dto["center"] = self.center()
        dto["dx"] = self.deltaX()
        dto["dy"] = self.deltaY()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setText(dto["text"])
        self.setCenter(dto["center"])
        self.setDeltaX(dto["dx"])
        self.setDeltaY(dto["dy"])

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

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        self.positionNotify(change)
        if (
            self.scene()
            and change == QGraphicsItem.ItemPositionChange
            and QApplication.mouseButtons() == Qt.LeftButton
        ):
            return QPointF(gui_utils.snap(value.x()), gui_utils.snap(value.y()))
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._on_item_move(value)
        if change == QGraphicsItem.ItemSceneChange:
            self._handler.on_scene_change(value)
        if change == QGraphicsItem.ItemZValueHasChanged:
            self._handler.on_zvalue_change()
        if change == QGraphicsItem.ItemSelectedHasChanged:
            is_selected = bool(value)
            self.setLive(is_selected)
        return super().itemChange(change, value)

    def _handle_selection_changed(self, is_selected):
        self.setLive(is_selected)

    def _recalculate(self):
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

        self.update()
        self.notify()

        self._updateHandles()

    def _updateHandles(self):
        x1, y1, x2, y2 = self._getCoordinates()
        self._handler.handle[1].setPos(x1, y1)
        self._handler.handle[2].setPos(x2, y1)
        self._handler.handle[3].setPos(x2, y2)
        self._handler.handle[4].setPos(x1, y2)

    def _getCoordinates(self):
        pos = self.pos()
        x1 = pos.x()
        y1 = pos.y()
        x2 = x1 + self._rect.width()
        y2 = y1 + self._rect.height()
        return x1, y1, x2, y2

    def setLive(self, is_live):
        """An element must stay live when the one or its handle were selected"""
        is_really_live = (
            is_live or self.isSelected() or self._handler.is_handle_selected()
        )
        self._is_live = is_really_live
        self._handler.setLive(is_really_live)

    def _on_item_move(self, position):
        self._recalculate()

    def calculateResizeHandlePosition(self, point: QPointF, handle: ResizeHandleItem):
        if not handle.isSelected() or handle.is_resizing or not self.isResizing():
            return point

        x1, y1, x2, y2 = self._getCoordinates()
        new_dx = self._dx
        new_dy = self._dy
        delta_dx = 0.0
        delta_dy = 0.0

        if handle == self._handler.handle[1]:
            shift_x = point.x() - x1
            shift_y = point.y() - y1
            new_dx = max(0.0, self._dx - shift_x)
            new_dy = max(0.0, self._dy - shift_y)
            delta_dx = new_dx - self._dx
            delta_dy = new_dy - self._dy
        elif handle == self._handler.handle[2]:
            shift_x = point.x() - x2
            shift_y = point.y() - y1
            new_dx = max(0.0, self._dx + shift_x)
            new_dy = max(0.0, self._dy - shift_y)
            delta_dy = new_dy - self._dy
        elif handle == self._handler.handle[3]:
            shift_x = point.x() - x2
            shift_y = point.y() - y2
            new_dx = max(0.0, self._dx + shift_x)
            new_dy = max(0.0, self._dy + shift_y)
        elif handle == self._handler.handle[4]:
            shift_x = point.x() - x1
            shift_y = point.y() - y2
            new_dx = max(0.0, self._dx - shift_x)
            new_dy = max(0.0, self._dy + shift_y)
            delta_dx = new_dx - self._dx

        if self._dx != new_dx or self._dy != new_dy:
            self._dx = new_dx
            self._dy = new_dy
            handle.is_resizing = True
            self._recalculate()
            if abs(delta_dx) + abs(delta_dy) > 0.0:
                self.moveBy(-delta_dx, -delta_dy)
            handle.is_resizing = False

        return handle.pos()

    def isResizing(self) -> bool:
        return not self.isSelected() and self._handler.isResizing()
