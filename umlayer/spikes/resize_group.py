import sys
from typing import Any

import PySide6.QtWidgets
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class GraphicsItem(QGraphicsItemGroup):

    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8

    handleSize = +12.0
    handleSpace = -4.0

    handleCursors = {
        handleTopLeft: Qt.SizeFDiagCursor,
        handleTopMiddle: Qt.SizeVerCursor,
        handleTopRight: Qt.SizeBDiagCursor,
        handleMiddleLeft: Qt.SizeHorCursor,
        handleMiddleRight: Qt.SizeHorCursor,
        handleBottomLeft: Qt.SizeBDiagCursor,
        handleBottomMiddle: Qt.SizeVerCursor,
        handleBottomRight: Qt.SizeFDiagCursor,
    }

    def __init__(self, x, y, w, h, parent=None):
        """
        Initialize the shape.
        """
        super().__init__(parent)
        self._rect = QGraphicsRectItem(x, y, w, h)
        self.handles = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.updateHandlesPos()

    def handleAt(self, point):
        """
        Returns the resize handle below the given point.
        """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return None

    def hoverMoveEvent(self, move_event):
        """
        Executed when the mouse moves over the shape (NOT PRESSED).
        """
        if self.isSelected():
            handle = self.handleAt(move_event.pos())
            cursor = Qt.ArrowCursor if handle is None else self.handleCursors[handle]
            self.setCursor(cursor)
        super().hoverMoveEvent(move_event)

    def hoverLeaveEvent(self, move_event):
        """
        Executed when the mouse leaves the shape (NOT PRESSED).
        """
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(move_event)

    def mousePressEvent(self, mouse_event):
        """
        Executed when the mouse is pressed on the item.
        """
        self.handleSelected = self.handleAt(mouse_event.pos())
        if self.handleSelected:
            self.mousePressPos = mouse_event.pos()
            self.mousePressRect = self.boundingRect()
        super().mousePressEvent(mouse_event)

    def mouseMoveEvent(self, mouse_event):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected is not None:
            self.interactiveResize(mouse_event.pos())
        else:
            super().mouseMoveEvent(mouse_event)

    def mouseReleaseEvent(self, mouse_event):
        """
        Executed when the mouse is released from the item.
        """
        super().mouseReleaseEvent(mouse_event)
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()

    def boundingRect(self):
        """
        Returns the bounding rect of the shape (including the resize handles).
        """
        o = self.handleSize + self.handleSpace
        return self._rect.rect().adjusted(-o, -o, o, o)

    def updateHandlesPos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handleSize
        b = self.boundingRect()
        self.handles[self.handleTopLeft] = QRectF(b.left(), b.top(), s, s)
        self.handles[self.handleTopMiddle] = QRectF(b.center().x() - s / 2, b.top(), s, s)
        self.handles[self.handleTopRight] = QRectF(b.right() - s, b.top(), s, s)
        self.handles[self.handleMiddleLeft] = QRectF(b.left(), b.center().y() - s / 2, s, s)
        self.handles[self.handleMiddleRight] = QRectF(b.right() - s, b.center().y() - s / 2, s, s)
        self.handles[self.handleBottomLeft] = QRectF(b.left(), b.bottom() - s, s, s)
        self.handles[self.handleBottomMiddle] = QRectF(b.center().x() - s / 2, b.bottom() - s, s, s)
        self.handles[self.handleBottomRight] = QRectF(b.right() - s, b.bottom() - s, s, s)

    def interactiveResize(self, mouse_pos):
        """
        Perform shape interactive resize.
        """
        offset = self.handleSize + self.handleSpace
        bounding_rect = self.boundingRect()
        rect = self._rect.rect()
        diff = QPointF(0, 0)

        self.prepareGeometryChange()

        if self.handleSelected == self.handleTopLeft:
            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.top()
            toX = fromX + mouse_pos.x() - self.mousePressPos.x()
            toY = fromY + mouse_pos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            bounding_rect.setLeft(toX)
            bounding_rect.setTop(toY)
            rect.setLeft(bounding_rect.left() + offset)
            rect.setTop(bounding_rect.top() + offset)
            self._rect.setRect(rect)

        elif self.handleSelected == self.handleTopMiddle:
            fromY = self.mousePressRect.top()
            toY = fromY + mouse_pos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            bounding_rect.setTop(toY)
            rect.setTop(bounding_rect.top() + offset)
            self._rect.setRect(rect)

        elif self.handleSelected == self.handleTopRight:
            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.top()
            toX = fromX + mouse_pos.x() - self.mousePressPos.x()
            toY = fromY + mouse_pos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            bounding_rect.setRight(toX)
            bounding_rect.setTop(toY)
            rect.setRight(bounding_rect.right() - offset)
            rect.setTop(bounding_rect.top() + offset)
            self._rect.setRect(rect)

        elif self.handleSelected == self.handleMiddleLeft:
            fromX = self.mousePressRect.left()
            toX = fromX + mouse_pos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            bounding_rect.setLeft(toX)
            rect.setLeft(bounding_rect.left() + offset)
            self._rect.setRect(rect)

        elif self.handleSelected == self.handleMiddleRight:
            fromX = self.mousePressRect.right()
            toX = fromX + mouse_pos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            bounding_rect.setRight(toX)
            rect.setRight(bounding_rect.right() - offset)
            self._rect.setRect(rect)

        elif self.handleSelected == self.handleBottomLeft:
            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mouse_pos.x() - self.mousePressPos.x()
            toY = fromY + mouse_pos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            bounding_rect.setLeft(toX)
            bounding_rect.setBottom(toY)
            rect.setLeft(bounding_rect.left() + offset)
            rect.setBottom(bounding_rect.bottom() - offset)
            self._rect.setRect(rect)

        elif self.handleSelected == self.handleBottomMiddle:
            fromY = self.mousePressRect.bottom()
            toY = fromY + mouse_pos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            bounding_rect.setBottom(toY)
            rect.setBottom(bounding_rect.bottom() - offset)
            self._rect.setRect(rect)

        elif self.handleSelected == self.handleBottomRight:
            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mouse_pos.x() - self.mousePressPos.x()
            toY = fromY + mouse_pos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            bounding_rect.setRight(toX)
            bounding_rect.setBottom(toY)
            rect.setRight(bounding_rect.right() - offset)
            rect.setBottom(bounding_rect.bottom() - offset)
            self._rect.setRect(rect)

        self.updateHandlesPos()

    def shape(self):
        """
        Returns the shape of this item as a QPainterPath in local coordinates.
        """
        path = QPainterPath()
        path.addRect(self._rect.rect())
        if self.isSelected():
            for shape in self.handles.values():
                path.addEllipse(shape)
        return path

    def paint(self, painter, option, widget=None):
        """
        Paint the node in the graphic view.
        """
        painter.setRenderHint(QPainter.Antialiasing)

        # draw item
        painter.setBrush(QBrush(QColor(195, 210, 213, 255)))
        painter.setPen(QPen(QColor(0, 0, 0), 1.0, Qt.SolidLine))
        painter.drawEllipse(self._rect.rect())

        if option.state & QStyle.State_Selected:
            # highlight selected item
            x, y = self._rect.rect().width(), self._rect.rect().height()
            painter.setPen(QPen(QColor(12, 27, 51, 255), 2, Qt.DotLine))
            painter.drawPolyline(QPolygon([QPoint(0, 0), QPoint(x, 0), QPoint(x, y), QPoint(0, y), QPoint(0, 0)]))

            # draw handles
            painter.setBrush(QBrush(QColor(12, 27, 51, 255)))
            painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            for handle, rect in self.handles.items():
                if self.handleSelected is None or handle == self.handleSelected:
                    painter.drawRect(rect)



    def itemChange(self, change: PySide6.QtWidgets.QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            print('selection', value)
        return super().itemChange(change, value)


def main():
    app = QApplication(sys.argv)

    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 680, 459)

    view = QGraphicsView()
    view.setDragMode(QGraphicsView.RubberBandDrag)
    view.setRubberBandSelectionMode(Qt.ContainsItemBoundingRect)
    view.setSceneRect(-1000, -1000, 2000, 2000)
    view.setScene(scene)

    item = GraphicsItem(0, 0, 300, 150)
    item.setPos(100, 100)
    scene.addItem(item)

    view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
    view.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()