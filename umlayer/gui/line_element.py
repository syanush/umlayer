"""Line element of the Use Case diagram"""

from PySide6.QtWidgets import *


class LineElement(QGraphicsItemGroup):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.items = [
            QGraphicsLineItem(0, 0, 50, 0)
        ]

        for item in self.items:
            self.addToGroup(item)
