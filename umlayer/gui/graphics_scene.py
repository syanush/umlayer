import logging

from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import UserElement, LineElement


class GraphicsScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def addUserElement(self, x: float, y: float):
        logging.info('Add user element')
        element = UserElement()
        element.setPos(x, y)
        element.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.addItem(element)

    def addLineElement(self):
        logging.info('Add line element')
        element = LineElement()
        element.setPos(50, 50)
        element.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.addItem(element)

    def addRectangle(self):
        logging.info('Add rectangle')

        rect = QGraphicsRectItem(0, 0, 200, 50)

        # Set the origin (position) of the rectangle in the scene.
        rect.setPos(50, 20)

        # Define the brush (fill).
        brush = QBrush(Qt.red)
        rect.setBrush(brush)

        # Define the pen (line)
        pen = QPen(Qt.cyan)
        pen.setWidth(10)
        rect.setPen(pen)

        rect.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.addItem(rect)
