from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class SimpleClassElement(QGraphicsItem):

    def __init__(self, x1: float, y1: float, x2: float, y2: float, parent=None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self._line = QGraphicsLineItem(x1, y1, x2, y2, parent=self)

        # self._grip1 = QGraphicsEllipseItem(x1, y1, 20, 20)
        # self._grip2 = QGraphicsEllipseItem(x1, y1, 20, 20)

        #self.setFlag(QGraphicsItem.ItemIsMovable, True)
        #self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self._line.setFlag(QGraphicsItem.ItemIsMovable, True)
        self._line.setFlag(QGraphicsItem.ItemIsSelectable, True)


    def boundingRect(self):
        return self._line.boundingRect()

    def paint(self, painter, option, widget=None) -> None:
        pass


class Resizer(QGraphicsObject):
    #resizeSignal = Signal(QPointF)
    signallo = Signal(QPointF)

    def __init__(self, rect=QRectF(0, 0, 20, 20), parent=None):
        super().__init__(parent)

        # self.signallo.connect(self.my_func)
        # self.signallo.emit(45)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.rect = rect

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        print('dot paint')
        if self.isSelected():
            pen = QPen()
            pen.setStyle(Qt.DotLine)
            painter.setPen(pen)
        painter.drawEllipse(self.rect)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            print(change)
            if self.isSelected():
                data = value - self.pos()
                if type(data) != QPointF:
                    raise Exception
                self.signallo.emit(data)
        return value




class SimpleClassElement1(QGraphicsItemGroup):
    """Simple class"""

    def __init__(self, x: float, y: float, w: float, h: float, text=None, contextMenu=None, parent=None):
        super().__init__(parent)

        self._context_menu = contextMenu

        self._rectangle = QGraphicsRectItem(0, 0, w, h, self)
        self.addToGroup(self._rectangle)

        self._text = QGraphicsTextItem(text or '')
        self.addToGroup(self._text)

        self.setPos(x, y)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.resizer = Resizer(parent=self)
        resizerWidth = self.resizer.rect.width() / 2
        resizerOffset = QPointF(resizerWidth, resizerWidth)
        self.resizer.setPos(self._rectangle.rect().bottomRight() - resizerOffset)
        #self.addToGroup(self.resizer)

        print('connect')
        self.resizer.signallo.connect(self.myResize)

        print(self.group())

    @Slot(QPointF)
    def myResize(self, change):
        print('resize', change)
        self._rectangle.setRect(self._rectangle.rect().adjusted(0, 0, change.x(), change.y()))
        self.prepareGeometryChange()
        self.update()

    def contextMenuEvent(self, event):
        # select current item
        self.scene().clearSelection()
        self.setSelected(True)

        self._my_context_menu.exec(event.screenPos())

    # def boundingRect(self) -> QRectF:
    #     return super().boundingRect()

    def _setSelectionColor(self, painter):
        #return
        if self.isSelected():
            self._rectangle.setBrush(QBrush(QColor(0, 0, 255, 15)))
            self._text.setDefaultTextColor(Qt.blue)
        else:
            self._rectangle.setBrush(QBrush(Qt.white))
            self._text.setDefaultTextColor(Qt.black)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        #self._setSelectionColor(painter)

        #textShift =  (self.boundingRect().width() - self._text.boundingRect().width()) / 2
        #self._text.setPos(textShift, 0)

        super().paint(painter, option, widget)

    def setText(self, text):
        self.text = text

    # def rect()
    #
    # def setRect(rect)
    #
    # def setRect(x, y, w, h)


class SimpleRectElement(QGraphicsRectItem):
    """Simple class"""

    def __init__(self, x: float, y: float, w: float, h: float, text=None, contextMenu=None, parent=None):
        super().__init__(parent)

        self._context_menu = contextMenu

        self._rectangle = self #QGraphicsRectItem(0, 0, w, h, self)

        self.setPos(x, y)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.resizer = Resizer(parent=self)
        resizerWidth = self.resizer.rect.width() / 2
        resizerOffset = QPointF(resizerWidth, resizerWidth)
        self.resizer.setPos(self._rectangle.rect().bottomRight() - resizerOffset)
        #self.addToGroup(self.resizer)

        print('connect')
        self.resizer.signallo.connect(self.myResize)

    @Slot(QPointF)
    def myResize(self, change):
        print('resize', change)
        self._rectangle.setRect(self._rectangle.rect().adjusted(0, 0, change.x(), change.y()))
        self.prepareGeometryChange()
        self.update()

    def contextMenuEvent(self, event):
        # select current item
        self.scene().clearSelection()
        self.setSelected(True)

        self._my_context_menu.exec(event.screenPos())

    # def boundingRect(self) -> QRectF:
    #     return super().boundingRect()

    def _setSelectionColor(self, painter):
        #return
        if self.isSelected():
            #painter.setPen(QPen(Qt.blue, 1))
            self._rectangle.setBrush(QBrush(QColor(0, 0, 255, 15)))
        else:
            #painter.setPen(QPen(Qt.black, 1))
            self._rectangle.setBrush(QBrush(Qt.white))

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        self._setSelectionColor(painter)

        super().paint(painter, option, widget)
