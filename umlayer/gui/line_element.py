"""Line element of the Use Case diagram"""

from PySide6.QtWidgets import *


class LineElement(QGraphicsItemGroup):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.items = [
            QGraphicsLineItem(-100, 100, 100, -100)
        ]
