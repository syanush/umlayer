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
        self._handler.handle[1] = ResizeHandleItem(Settings.RESIZE_HANDLE_SIZE, self.topLeftResize)
        self._handler.handle[2] = ResizeHandleItem(Settings.RESIZE_HANDLE_SIZE, self.topRightResize)
        self._handler.handle[3] = ResizeHandleItem(Settings.RESIZE_HANDLE_SIZE, self.bottomRightResize)
        self._handler.handle[4] = ResizeHandleItem(Settings.RESIZE_HANDLE_SIZE, self.bottomLeftResize)

        self._handler.on_zvalue_change()

        for handle in self._handler.handle.values():
            handle.selection_changed_signal.connect(self._handle_selection_changed)

        self.setLive(False)

        self._text_item = TextItem(center=center, parent=self)
        self.recalculate()

    def text(self):
        return self._text

    def setText(self, text: str):
        if self._text != text:
            self._text = text
            self.recalculate()

    def center(self):
        return self._center

    def setCenter(self, center: bool):
        if self._center != center:
            self._center = center
            self.recalculate()

    def deltaX(self):
        return self._dx

    def setDeltaX(self, dx):
        if self._dx != dx:
            self._dx = dx
            # self.recalculate()

    def deltaY(self):
        return self._dy

    def setDeltaY(self, dy):
        if self._dy != dy:
            self._dy = dy
            # self.recalculate()

    def rect(self):
        x1 = self.pos().x()
        y1 = self.pos().y()
        return QRectF(x1, y1, self._rect.width(), self._rect.height())

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

    def recalculate(self):
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
        p1 = self.rect().topLeft()
        p2 = self.rect().bottomRight()
        x1 = p1.x()
        y1 = p1.y()
        x2 = p2.x()
        y2 = p2.y()
        return x1, y1, x2, y2

    def setLive(self, is_live):
        """An element must stay live when the one or its handle were selected"""
        is_really_live = (
            is_live or self.isSelected() or self._handler.is_handle_selected()
        )
        self._is_live = is_really_live
        self._handler.setLive(is_really_live)

    def _on_item_move(self, position):
        self.recalculate()

    def leftX(self, point):
        dx = max(0.0, self.deltaX() - point.x() + self.rect().topLeft().x())
        return dx, self.deltaX() - dx

    def rightX(self, point):
        dx = max(0.0, self.deltaX() + point.x() - self.rect().bottomRight().x())
        return dx, 0.0

    def topY(self, point):
        dy = max(0.0, self.deltaY() - point.y() + self.rect().topLeft().y())
        return dy, self.deltaY() - dy

    def bottomY(self, point):
        dy = max(0.0, self.deltaY() + point.y() - self.rect().bottomRight().y())
        return dy, 0.0

    def doResize(self, dx, dy, rx, ry, handle):
        if self.deltaX() != dx or self.deltaY() != dy:
            self.setDeltaX(dx)
            self.setDeltaY(dy)
            handle.is_resizing = True
            self.recalculate()
            self.moveBy(rx, ry)
            handle.is_resizing = False
        return handle.pos()

    def topLeftResize(self, point: QPointF, handle: ResizeHandleItem):
        if not self.isResizing():
            return point
        dx, rx = self.leftX(point)
        dy, ry = self.topY(point)
        return self.doResize(dx, dy, rx, ry, handle)

    def topRightResize(self, point: QPointF, handle: ResizeHandleItem):
        if not self.isResizing():
            return point
        dx, rx = self.rightX(point)
        dy, ry = self.topY(point)
        return self.doResize(dx, dy, rx, ry, handle)

    def bottomRightResize(self, point: QPointF, handle: ResizeHandleItem):
        if not self.isResizing():
            return point
        dx, rx = self.rightX(point)
        dy, ry = self.bottomY(point)
        return self.doResize(dx, dy, rx, ry, handle)

    def bottomLeftResize(self, point: QPointF, handle: ResizeHandleItem):
        if not self.isResizing():
            return point
        dx, rx = self.leftX(point)
        dy, ry = self.bottomY(point)
        return self.doResize(dx, dy, rx, ry, handle)

    def isResizing(self) -> bool:
        return not self.isSelected() and self._handler.isResizing()
