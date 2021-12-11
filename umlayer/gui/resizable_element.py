import abc

from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QGraphicsItem, QApplication

from umlayer.gui import BaseElement, Handler, ResizeHandleItem, Settings, gui_utils


class ResizableElement(BaseElement):
    def __init__(self, dx: float = 0, dy: float = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # serializable data
        self._dx = dx  # must be non-negative
        self._dy = dy
        # end of serializable data

        self._handler = Handler(item=self)
        self._createHandles()

    def _createHandles(self):
        self._handler.handle[1] = ResizeHandleItem(
            Settings.RESIZE_HANDLE_SIZE,
            self.calculateTopLeftHandlePositionChange,
            name="1",
        )
        self._handler.handle[2] = ResizeHandleItem(
            Settings.RESIZE_HANDLE_SIZE,
            self.calculateTopRightHandlePositionChange,
            name="2",
        )
        self._handler.handle[3] = ResizeHandleItem(
            Settings.RESIZE_HANDLE_SIZE,
            self.calculateBottomRightHandlePositionChange,
            name="3",
        )
        self._handler.handle[4] = ResizeHandleItem(
            Settings.RESIZE_HANDLE_SIZE,
            self.calculateBottomLeftHandlePositionChange,
            name="4",
        )

        self._handler.on_zvalue_change()

        for handle in self._handler.handle.values():
            handle.selection_changed_signal.connect(self.onHandleSelectionChanged)

    def deltaX(self):
        return self._dx

    def setDeltaX(self, dx):
        if self._dx != dx:
            self._dx = dx

    def deltaY(self):
        return self._dy

    def setDeltaY(self, dy):
        if self._dy != dy:
            self._dy = dy

    @abc.abstractmethod
    def rect(self) -> QRectF:
        raise NotImplementedError

    def sceneRect(self):
        x1 = self.pos().x()
        y1 = self.pos().y()
        return QRectF(x1, y1, self.rect().width(), self.rect().height())

    def setLive(self, is_live):
        """An element must stay live when the one or its handle were selected"""
        is_really_live = (
            is_live or self.isSelected() or self._handler.is_handle_selected()
        )
        self._is_live = is_really_live
        self._handler.setLive(is_really_live)

    def toDto(self):
        dto = super().toDto()
        dto["dx"] = self.deltaX()
        dto["dy"] = self.deltaY()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setDeltaX(dto["dx"])
        self.setDeltaY(dto["dy"])

    @abc.abstractmethod
    def recalculate(self):
        raise NotImplementedError

    def updateHandlePositions(self):
        x1 = self.sceneRect().topLeft().x()
        y1 = self.sceneRect().topLeft().y()
        x2 = self.sceneRect().bottomRight().x()
        y2 = self.sceneRect().bottomRight().y()
        self._handler.handle[1].setPos(x1, y1)
        self._handler.handle[2].setPos(x2, y1)
        self._handler.handle[3].setPos(x2, y2)
        self._handler.handle[4].setPos(x1, y2)

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

    def onItemPositionHasChanged(self, position):
        self.recalculate()

    def onItemSceneChange(self, value) -> None:
        self._handler.on_scene_change(value)

    def onItemZValueHasChanged(self, value):
        self._handler.on_zvalue_change()

    def onItemSelectedHasChanged(self, value):
        is_selected = bool(value)
        self.setLive(is_selected)

    def onHandleSelectionChanged(self, is_selected):
        self.setLive(is_selected)

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
            # print(handle, "isPositionChangeAccepted", position)
            # the handle that resizes the element changes position
            return position

        if self.isMoveForbidden(handle):
            # print(handle, "isMoveForbidden", handle.pos())
            # the handle position stays unchanged because conditions for resize are not met
            return handle.pos()

        if not self.isResizeAllowed(handle):
            # print(handle, "isResizeAllowed", position)
            # the handle does not take part in resize
            return position

        size_x, shift_x = calculate_x_change(position)
        size_y, shift_y = calculate_y_change(position)

        if self.deltaX() != size_x or self.deltaY() != size_y:
            # print(handle, "RESIZE")
            handle.setPositionChangeAccepted(True)
            self.setDeltaX(size_x)
            self.setDeltaY(size_y)
            self.recalculate()
            self.moveBy(shift_x, shift_y)
            handle.setPositionChangeAccepted(False)
        # else:
        #     print(handle, "NO RESIZE")
        # print(handle, handle.pos())
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

    def calculateLeftXChange(self, position):
        size_x = max(0.0, self.deltaX() - position.x() + self.sceneRect().topLeft().x())
        shift_x = self.deltaX() - size_x
        return size_x, shift_x

    def calculateRightXChange(self, position):
        # print("calculateRightXChange")
        # print(f"{self.deltaX()=}")
        # print(f"{position.x()=}")
        # print(f"{self.sceneRect().bottomRight().x()=}")
        size_x = max(
            0.0, self.deltaX() + position.x() - self.sceneRect().bottomRight().x()
        )
        shift_x = 0.0
        # print(f"{size_x=}")
        return size_x, shift_x

    def calculateTopYChange(self, position):
        size_y = max(0.0, self.deltaY() - position.y() + self.sceneRect().topLeft().y())
        shift_y = self.deltaY() - size_y
        return size_y, shift_y

    def calculateBottomYChange(self, position):
        size_y = max(
            0.0, self.deltaY() + position.y() - self.sceneRect().bottomRight().y()
        )
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
