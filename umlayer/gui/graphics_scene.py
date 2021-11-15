import logging

from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import (
    UserElement,
    SimpleClassElement,
    Resizer,
    SimpleRectElement,
    UseCaseElement,
    PackageElement,
    diagram_pen,
    diagram_brush
)


class GraphicsScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def addUserElement(self, x: float, y: float):
        logging.info('Add user element')
        item = UserElement()
        item.setPos(x, y)
        self.addItem(item)

    def addSimpleClass(self, x1: float, y1: float, x2: float, y2: float):
        logging.info('Add Simple Class')
        self.addItem(SimpleClassElement(x1, y1, x2, y2))

    def addResizer(self):
        r = Resizer(parent=self)
        self.addItem(r)
        r.setPos(20, 20)

    def addUseCase(self):
        # pen = QPen()
        #
        # color = QColor(15, 100, 29, 255)
        # bg_color = Qt.white
        # pen.setStyle(Qt.SolidLine)
        # pen.setColor(color)
        #
        # brush = QBrush()
        # brush.setColor(bg_color)
        #
        # painter.setPen(pen)

        item = UseCaseElement(20, 20, 100, 50)
        self.addItem(item)

    def addPackageElement(self, x: float, y: float):
        item = PackageElement()
        item.setPen(diagram_pen)
        item.setBrush(diagram_brush)
        item.setPos(x, y)
        self.addItem(item)
