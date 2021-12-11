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

        self._text_item = TextItem(center=center, parent=self)
        self._handler = Handler(item=self)
        self._createHandles()
        self.setLive(False)

    def _createHandles(self):
        self._handler.handle[1] = ResizeHandleItem(
            Settings.RESIZE_HANDLE_SIZE, self.calculateTopLeftHandlePositionChange
        )
        self._handler.handle[2] = ResizeHandleItem(
            Settings.RESIZE_HANDLE_SIZE, self.calculateTopRightHandlePositionChange
        )
        self._handler.handle[3] = ResizeHandleItem(
            Settings.RESIZE_HANDLE_SIZE, self.calculateBottomRightHandlePositionChange
        )
        self._handler.handle[4] = ResizeHandleItem(
            Settings.RESIZE_HANDLE_SIZE, self.calculateBottomLeftHandlePositionChange
        )

        self._handler.on_zvalue_change()

        for handle in self._handler.handle.values():
            handle.selection_changed_signal.connect(self.onHandleSelectionChanged)

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
            self.recalculate()

    def deltaY(self):
        return self._dy

    def setDeltaY(self, dy):
        if self._dy != dy:
            self._dy = dy
            self.recalculate()

    def rect(self):
        x1 = self.pos().x()
        y1 = self.pos().y()
        return QRectF(x1, y1, self._rect.width(), self._rect.height())

    def setLive(self, is_live):
        """An element must stay live when the one or its handle were selected"""
        is_really_live = (
            is_live or self.isSelected() or self._handler.is_handle_selected()
        )
        self._is_live = is_really_live
        self._handler.setLive(is_really_live)
        self.recalculate()

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
        if self.scene() and change == QGraphicsItem.ItemPositionChange:
            value = self.calculateItemPositionChange(value)
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.onItemPositionHasChanged(value)
        if change == QGraphicsItem.ItemSceneChange:
            self.onItemSceneChange(value)
        if change == QGraphicsItem.ItemZValueHasChanged:
            self.onItemZValueHasChanged(value)
        if change == QGraphicsItem.ItemSelectedHasChanged:
            self.onItemSelectedHasChanged(value)
        return super().itemChange(change, value)

    def calculateItemPositionChange(self, position):
        if QApplication.mouseButtons() == Qt.LeftButton:
            return gui_utils.snap_position(position)
        return position

    def onItemSceneChange(self, value) -> None:
        self._handler.on_scene_change(value)

    def onItemZValueHasChanged(self, value):
        self._handler.on_zvalue_change()

    def onItemSelectedHasChanged(self, value):
        is_selected = bool(value)
        self.setLive(is_selected)

    def onHandleSelectionChanged(self, is_selected):
        self.setLive(is_selected)

    def recalculate(self):
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

    def updateHandlePositions(self):
        x1 = self.rect().topLeft().x()
        y1 = self.rect().topLeft().y()
        x2 = self.rect().bottomRight().x()
        y2 = self.rect().bottomRight().y()
        self._handler.handle[1].setPos(x1, y1)
        self._handler.handle[2].setPos(x2, y1)
        self._handler.handle[3].setPos(x2, y2)
        self._handler.handle[4].setPos(x1, y2)

    def onItemPositionHasChanged(self, position):
        self.recalculate()

    def calculateHandlePositionChange(
        self,
        handle: ResizeHandleItem,
        position: QPointF,
        calculate_x_change,
        calculate_y_change,
    ):
        """Calculates and sets the actual handle position for ItemPositionChange of the handle

        handle - the handle that is used for resize.
        position - proposed position for handle to move to.
        calculate_x_change, calculate_y_change - methods for calculating size and position changes.
        """

        # The order of checks is important

        if handle.isPositionChangeAccepted():
            # the handle that resizes the element changes position
            return position

        if self.isMoveForbidden(handle):
            # the handle position stays unchanged because conditions for resize are not met
            return handle.pos()

        if not self.isResizeAllowed(handle):
            # the handle does not take part in resize
            return position

        size_x, shift_x = calculate_x_change(position)
        size_y, shift_y = calculate_y_change(position)

        if self.deltaX() != size_x or self.deltaY() != size_y:
            handle.setPositionChangeAccepted(True)
            self.setDeltaX(size_x)
            self.setDeltaY(size_y)
            self.moveBy(shift_x, shift_y)
            handle.setPositionChangeAccepted(False)
        return handle.pos()  # the handle position has changed

    def calculateTopLeftHandlePositionChange(
        self, handle: ResizeHandleItem, position: QPointF
    ):
        return self.calculateHandlePositionChange(
            handle, position, self.calculateLeftXChange, self.calculateTopYChange
        )

    def calculateTopRightHandlePositionChange(
        self, handle: ResizeHandleItem, position: QPointF
    ):
        return self.calculateHandlePositionChange(
            handle, position, self.calculateRightXChange, self.calculateTopYChange
        )

    def calculateBottomRightHandlePositionChange(
        self, handle: ResizeHandleItem, position: QPointF
    ):
        return self.calculateHandlePositionChange(
            handle, position, self.calculateRightXChange, self.calculateBottomYChange
        )

    def calculateBottomLeftHandlePositionChange(
        self, handle: ResizeHandleItem, position: QPointF
    ):
        return self.calculateHandlePositionChange(
            handle, position, self.calculateLeftXChange, self.calculateBottomYChange
        )

    def calculateLeftXChange(self, point):
        size_x = max(0.0, self.deltaX() - point.x() + self.rect().topLeft().x())
        shift_x = self.deltaX() - size_x
        return size_x, shift_x

    def calculateRightXChange(self, point):
        size_x = max(0.0, self.deltaX() + point.x() - self.rect().bottomRight().x())
        shift_x = 0.0
        return size_x, shift_x

    def calculateTopYChange(self, point):
        size_y = max(0.0, self.deltaY() - point.y() + self.rect().topLeft().y())
        shift_y = self.deltaY() - size_y
        return size_y, shift_y

    def calculateBottomYChange(self, point):
        size_y = max(0.0, self.deltaY() + point.y() - self.rect().bottomRight().y())
        shift_y = 0.0
        return size_y, shift_y

    def isResizeAllowed(self, handle: ResizeHandleItem) -> bool:
        """Indicates when element resizing by dragging the handle is allowed.

        Conditions:
        1) Left mouse button must be pressed.
        2) The element must be deselected.
        3) The handle must be selected.
        4) Exactly one of all handles must be selected.
        """
        return (
            QApplication.mouseButtons() == Qt.LeftButton
            and not self.isSelected()
            and handle.isSelected()
            and self._handler.isResizing()
        )

    def isMoveForbidden(self, handle: ResizeHandleItem) -> bool:
        """Indicates the state when the handle should not change position

        Conditions:
        1) Left mouse button must be pressed.
        2) The element must be deselected.
        3) The handle must be selected.
        4) More than one handle are selected.
        """

        return (
            QApplication.mouseButtons() == Qt.LeftButton
            and not self.isSelected()
            and handle.isSelected()
            and not self._handler.isResizing()
        )
