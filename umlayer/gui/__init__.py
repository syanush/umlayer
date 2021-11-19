from PySide6.QtGui import *

element_font = QFont('Monospace', 9)
#element_font = QFont('Serif', 9)
#element_font = QFont('SansSerif', 9)
element_font.setStyleHint(QFont.TypeWriter)

element_color = Qt.black
element_brush_color = Qt.white
element_pen = QPen(element_color, 1, Qt.SolidLine)
element_brush = QBrush(QColor(0, 0, 0, 0))

highlight_color = QColor(12, 27, 51, 0)
highlight_pen = QPen(Qt.black, 3, Qt.DotLine)
highlight_brush = QBrush(QColor(0, 0, 0, 0))

# order is important
from .base_element import BaseElement, Abilities
from .text_item import TextItem
from .text_element import TextElement
from .actor_element import ActorElement
from .package_element import PackageElement
from .ellipse_element import EllipseElement
from .note_element import NoteElement
from .class_element import ClassElement
from .handle_item import HandleItem
from .line_element import LineElement

from .graphics_scene import GraphicsScene
from .graphics_view import GraphicsView
from .standard_item_model import StandardItemModel
from .tree_view import TreeView
from .gui_logic import GuiLogic
from .actions import Actions

from .mainwindow import MainWindow
from .app import UMLayerApplication
