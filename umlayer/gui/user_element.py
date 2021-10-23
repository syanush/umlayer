"""User element of the Use Case diagram"""

from PySide6.QtWidgets import *


class UserElement(QGraphicsItemGroup):
    def __init__(self, parent=None):
        super().__init__(parent)

        items = (
            QGraphicsEllipseItem(0, 0, 20, 20),
            QGraphicsLineItem(10, 20, 10, 45),  # vertical line
            QGraphicsLineItem(-5, 25, 25, 25),  # horizontal line
            QGraphicsLineItem(10, 45, -5, 65),  # left leg
            QGraphicsLineItem(10, 45, 25, 65),  # right leg
        )

        for item in items:
            self.addToGroup(item)
