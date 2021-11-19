from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Resizer(QGraphicsObject):
    resizeSignal = Signal(QPointF)

    def __init__(self, x, y, size, parent=None) -> None:
        super().__init__(parent)

        self.rect = QRectF(x, y, size, size)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self.setAcceptHoverEvents(True)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            pen = QPen()
            pen.setStyle(Qt.DotLine)
            painter.setPen(pen)
        painter.drawEllipse(self.rect)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            if self.isSelected():
                data = value - self.pos()
                self.resizeSignal.emit(data)
        return value


class UseCaseElement(QGraphicsObject):

    def __init__(self, x, y, w, h, parent=None) -> None:
        super().__init__(parent)
        self._border = QGraphicsRectItem(x, y, w, h, parent=self)
        self._border.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self._border.setFlag(QGraphicsItem.ItemIsMovable, True)
        self._grip = Resizer(x + w - 10, y + h - 10, 20, self._border)
        self._grip.resizeSignal.connect(self.myResize)

    def boundingRect(self) -> QRectF:
        return self._border.boundingRect()

    def paint(self, painter, option, widget=None) -> None:
        """no super"""
        pass

    def setSelected(self, selected: bool) -> None:
        print("selected!")
        super().setSelected(selected)

    @Slot(QPointF)
    def myResize(self, change):
        dw, dh = change.x(), change.y()
        old = self._border.rect()
        # adjusted: Returns a new rectangle with dx1, dy1, dx2 and dy2 added
        # to the existing coordinates of this rectangle.
        new = old.adjusted(0, 0, dw, dh)
        print('resize', dw, dh, old, new)
        if new.width() > 20 and new.height() > 20:
            self._border.setRect(new)
            self.prepareGeometryChange()
            self.update()





