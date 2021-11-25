from enum import Enum

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from . import *


class LineType(Enum):
    Solid = 0
    Dash = 1
    Dot = 2


class TipType(Enum):
    Empty = 0
    Arrow = 1
    HollowTriangle = 2
    FullTriangle = 3
    HollowDiamond = 4
    FullDiamond = 5


class LineElement(QGraphicsItem, BaseElement):
    def __init__(self, x1: float = 0, y1: float = 0, x2: float = 0, y2: float = 0, text: str = None, parent=None):
        super().__init__(parent)
        BaseElement.__init__(self)
        self._abilities = {Abilities.EDITABLE_TEXT}

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self._handle1 = HandleItem(10, parent=self)
        self._handle1.position_changed_signal.connect(self._handle1_position_changed)
        self._handle1.selection_changed_signal.connect(self._handle_selection_changed)
        self._handle1.setSelected(False)

        self._handle2 = HandleItem(10, parent=self)
        self._handle2.position_changed_signal.connect(self._handle2_position_changed)
        self._handle2.selection_changed_signal.connect(self._handle_selection_changed)
        self._handle2.setSelected(False)

        self.stroker = QPainterPathStroker()
        self.stroker.setWidth(15)

        self._text = text or ''
        self._point1 = QPointF(x1, y1)
        self._point2 = QPointF(x2, y2)
        self._line_type = LineType.Solid
        self._tip1: TipType = TipType.Empty
        self._tip2: TipType = TipType.Empty
        self._tip1_figure: Tip = NoTip()
        self._tip2_figure: Tip = NoTip()

        self.setLive(False)
        self._recalculate()

    def text(self):
        return self._text

    def setText(self, text: str):
        if self._text != text:
            self._text = text
            self._recalculate()

    def point1(self):
        return self._point1

    def setPoint1(self, x1: float, y1: float):
        point1 = QPointF(x1, y1)
        if self._point1 != point1:
            self._point1 = point1
            self._recalculate()

    def point2(self):
        return self._point2

    def setPoint2(self, x2, y2):
        point2 = QPointF(x2, y2)
        if self._point2 != point2:
            self._point2 = point2
            self._recalculate()

    def toDto(self):
        dto = super().toDto()
        dto['x1'] = self.point1().x()
        dto['y1'] = self.point1().y()
        dto['x2'] = self.point2().x()
        dto['y2'] = self.point2().y()
        dto['text'] = self.text()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setPoint1(dto['x1'], dto['y1'])
        self.setPoint2(dto['x2'], dto['y2'])
        self.setText(dto['text'])

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        return self._shape_path

    _pen_style_from_line_type = {
        LineType.Solid: Qt.SolidLine,
        LineType.Dash: Qt.DashLine,
        LineType.Dot: Qt.DotLine,
    }

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None) -> None:
        painter.setRenderHint(QPainter.Antialiasing)

        x1 = self._tip1_figure.point().x()
        y1 = self._tip1_figure.point().y()
        x2 = self._tip2_figure.point().x()
        y2 = self._tip2_figure.point().y()

        pen = Settings.LINE_SELECTED_PEN if self.isSelected() else Settings.LINE_NORMAL_PEN

        line_pen = QPen(pen)
        line_pen_style = self._pen_style_from_line_type[self._line_type]
        line_pen.setStyle(line_pen_style)

        painter.setPen(line_pen)
        painter.drawLine(x1, y1, x2, y2)

        painter.setPen(pen)
        if self._tip1 in [TipType.FullTriangle, TipType.FullDiamond]:
            painter.setBrush(QBrush(Qt.black))
        else:
            painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self._tip1_figure.paint(painter)

        if self._tip2 in [TipType.FullTriangle, TipType.FullDiamond]:
            painter.setBrush(QBrush(Qt.black))
        else:
            painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self._tip2_figure.paint(painter)

        # painter.drawPath(self.shape())

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        self.positionNotify(change)
        if self.scene() and \
                change == QGraphicsItem.ItemPositionChange and \
                QApplication.mouseButtons() == Qt.LeftButton:
            return QPointF(gui_utils.snap(value.x()), gui_utils.snap(value.y()))
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            is_selected = bool(value)
            self.prepareGeometryChange()
            self.setLive(is_selected)
        return super().itemChange(change, value)

    def setLive(self, is_live):
        self._is_live = is_live
        self._handle1.setLive(is_live)
        self._handle2.setLive(is_live)
        self._recalculate()

    def _handle_selection_changed(self, is_selected):
        self.setLive(is_selected)

    def _handle1_position_changed(self, point):
        self.setPoint1(point.x(), point.y())

    def _handle2_position_changed(self, point):
        self.setPoint2(point.x(), point.y())

    _tip_class_from_tip_type = {
        TipType.Empty: NoTip,
        TipType.Arrow: ArrowTip,
        TipType.HollowTriangle: TriangleTip,
        TipType.FullTriangle: TriangleTip,
        TipType.HollowDiamond: DiamondTip,
        TipType.FullDiamond: DiamondTip,
    }

    def _recalculate(self):
        self.prepareGeometryChange()
        self._parse_text()

        x1 = self.point1().x()
        y1 = self.point1().y()
        x2 = self.point2().x()
        y2 = self.point2().y()

        tip1_class = self._tip_class_from_tip_type[self._tip1]
        self._tip1_figure = tip1_class()
        self._tip1_figure.recalculate(self.point1(), self.point2())

        tip2_class = self._tip_class_from_tip_type[self._tip2]
        self._tip2_figure = tip2_class()
        self._tip2_figure.recalculate(self.point2(), self.point1())

        self._handle1.setPos(self.point1())
        self._handle2.setPos(self.point2())

        # IMPORTANT: width and height of the bounding box must be non-negative,
        # to remove painting artifacts
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x1 - x2)
        h = abs(y1 - y2)

        tip_size = max(self._tip1_figure.tip_size, self._tip2_figure.tip_size)
        self._bounding_rect = QRectF(
            x - tip_size,
            y - tip_size,
            w + 2 * tip_size,
            h + 2 * tip_size
        )

        path = QPainterPath()
        path.moveTo(self._handle1.pos())
        path.lineTo(self._handle2.pos())
        path.lineTo(self._handle1.pos())
        self._shape_path = self.stroker.createStroke(path)

        self.update()

    def _parse_text(self):
        """Parse

        Every line of text is either command or text for central label

        """
        label_lines = []
        lines = self.text().split('\n')
        for line in lines:
            if len(line) >= 4 and line[:3] == 'lt=':
                self.set_line_type(line[3:])
            else:
                label_lines.append(line)
        self._label_text = '\n'.join(label_lines)

    _tip_types = [TipType.Empty, TipType.Arrow, TipType.HollowTriangle,
                  TipType.FullTriangle, TipType.HollowDiamond, TipType.FullDiamond]

    _tip1_type_from_txt = dict(zip(['', '<', '<<', '<<<', '<<<<', '<<<<<'], _tip_types))
    _tip2_type_from_txt = dict(zip(['', '>', '>>', '>>>', '>>>>', '>>>>>'], _tip_types))

    _lt_from_splitter = {
        '-': LineType.Solid,
        '.': LineType.Dash,
        '..': LineType.Dot,
    }

    def set_line_type(self, txt: str):
        """Parse line type"""

        if txt.find('-') >= 0:
            splitter = '-'
        elif txt.find('..') >= 0:
            splitter = '..'
        elif txt.find('.') >= 0:
            splitter = '.'
        else:
            splitter = '-'

        self._line_type = self._lt_from_splitter[splitter]
        tips = txt.split(splitter)

        self._tip1 = TipType.Empty
        if len(tips) > 0:
            self._tip1 = self._tip1_type_from_txt.get(tips[0]) or TipType.Empty

        self._tip2 = TipType.Empty
        if len(tips) > 1:
            self._tip2 = self._tip2_type_from_txt.get(tips[1]) or TipType.Empty

        # print(self._tip1, self._line_type, self._tip2)
