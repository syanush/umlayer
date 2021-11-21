from PySide6.QtGui import *


class Settings:
    BLOCK_SIZE = 10
    GRID_PEN = QPen(Qt.gray, 1, Qt.SolidLine)
    ACTOR_ELEMENT_PEN = QPen(QColor(255, 255, 255, 255), 3)
    HANDLE_NORMAL_PEN = QPen(Qt.black, 1)
    HANDLE_SELECTED_PEN = QPen(Qt.blue, 1)

    ELEMENT_PADDING = 5
    HANDLE_MIN2 = 20

    LINE_DIAMETER = 40
    LINE_NORMAL_PEN = QPen(Qt.black, 1)
    LINE_SELECTED_PEN = QPen(Qt.blue, 1)

    NOTE_DELTA = 15

    element_font = QFont('Monospace', 9)
    # element_font = QFont('Serif', 9)
    # element_font = QFont('SansSerif', 9)
    element_font.setStyleHint(QFont.TypeWriter)

    element_color = Qt.black
    element_brush_color = Qt.white
    element_pen = QPen(element_color, 1, Qt.SolidLine)
    element_brush = QBrush(QColor(0, 0, 0, 0))

    highlight_color = QColor(12, 27, 51, 0)
    highlight_pen = QPen(Qt.black, 3, Qt.DotLine)
    highlight_brush = QBrush(QColor(0, 0, 0, 0))
