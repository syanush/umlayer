from PySide6.QtGui import *

diagram_font = QFont('Monospace')
diagram_font.setStyleHint(QFont.TypeWriter)
# diagram_color = QColor(195, 210, 213, 255)
# diagram_pen = QPen(diagram_color, 1, Qt.SolidLine)
# diagram_brush = QBrush(diagram_color)

item_color = Qt.black
item_brush_color = Qt.white
item_pen = QPen(item_color, 1, Qt.SolidLine)
item_brush = QBrush(item_brush_color)

highlight_color = QColor(12, 27, 51, 20)
highlight_pen = QPen(Qt.black, 3, Qt.DotLine)
highlight_brush = QBrush(highlight_color)

from .user_element import UserElement
from .simple_class_element import SimpleClassElement, Resizer, SimpleRectElement
from .line_element import LineElement
from .use_case_element import UseCaseElement
from .package_element import PackageElement
from .ellipse_element import EllipseElement

from .graphics_scene import GraphicsScene
from .graphics_view import GraphicsView
from .standard_item_model import StandardItemModel
from .tree_view import TreeView
from .gui_logic import GuiLogic
from .actions import Actions

from .mainwindow import MainWindow
from .app import UMLayerApplication
