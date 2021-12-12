from enum import Enum

from PySide6.QtCore import Qt, QPointF, QRectF, QLineF
from PySide6.QtGui import QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsScene,
    QStyleOptionGraphicsItem,
)

from . import (
    gui_utils,
    Abilities,
    BaseElement,
    Settings,
    Handler,
    NoTip,
    Tip,
    LineHandleItem,
    ArrowTip,
    TriangleTip,
    DiamondTip,
    HalfTriangleTip,
)


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
    FullHalfTriangle = 6


class LineElement(BaseElement):
    def __init__(
        self,
        x1: float = 0,
        y1: float = 0,
        x2: float = 0,
        y2: float = 0,
        text: str = None,
        parent=None,
    ):
        super().__init__(parent=parent)
        self._abilities = {Abilities.EDITABLE_TEXT}

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self._text = text or ""

        self._line_type = LineType.Solid
        self._tip1: TipType = TipType.Empty
        self._tip2: TipType = TipType.Empty
        self._tip1_figure: Tip = NoTip()
        self._tip2_figure: Tip = NoTip()

        self._handler = Handler(self)
        self._createHandles()

        self._isPositionChangeAccepted = False
        self._pos1 = QPointF(x1, y1)
        self._pos2 = QPointF(x2, y2)
        self.setLive(False)
        self.recalculate()

    def _createHandles(self):
        self._handler.handle[1] = LineHandleItem(
            Settings.LINE_HANDLE_SIZE,
            self.calculateHandlePositionChange,
            name="1",
        )
        self._handler.handle[2] = LineHandleItem(
            Settings.LINE_HANDLE_SIZE,
            self.calculateHandlePositionChange,
            name="2",
        )

        self.onItemZValueHasChanged()

        for handle in self._handler.handle.values():
            handle.selection_changed_signal.connect(self._handle_selection_changed)

    def text(self):
        return self._text

    def setText(self, text: str):
        if self._text == text:
            return
        self._text = text
        self.recalculate()

    def point1(self):
        return self._pos1

    def setPoint1(self, position: QPointF):
        """Sets external coordinates of the first point"""
        if self._pos1 == position:
            return
        self._pos1 = position
        self.recalculate()

    def point2(self):
        return self._pos2

    def setPoint2(self, position: QPointF):
        """Sets external coordinates of the second point"""
        if self._pos2 == position:
            return
        self._pos2 = position
        self.recalculate()

    def rect(self) -> QRectF:
        return self._rect

    def selectAll(self):
        self.setSelected(True)
        self._handler.selectAll()

    def setLive(self, is_live):
        """A line must stay live when the line or its handle were selected"""
        is_really_live = (
            is_live or self.isSelected() or self._handler.is_handle_selected()
        )
        self._is_live = is_really_live
        self._handler.setLive(is_really_live)

    def toDto(self):
        dto = super().toDto()
        dto["x1"] = self.point1().x()
        dto["y1"] = self.point1().y()
        dto["x2"] = self.point2().x()
        dto["y2"] = self.point2().y()
        dto["text"] = self.text()
        return dto

    def setFromDto(self, dto: dict):
        super().setFromDto(dto)
        self.setPoint1(QPointF(dto["x1"], dto["y1"]))
        self.setPoint2(QPointF(dto["x2"], dto["y2"]))
        self.setText(dto["text"])

    def setAllPositionChangeAccepted(self, accepted: bool):
        self.setPositionChangeAccepted(accepted)
        self._handler.handle[1].setPositionChangeAccepted(accepted)
        self._handler.handle[2].setPositionChangeAccepted(accepted)

    def recalculate(self):
        self.notify()
        self.prepareGeometryChange()

        self._parse_text()

        position = QPointF(
            min(self._pos1.x(), self._pos2.x()), min(self._pos1.y(), self._pos2.y())
        )

        if position != self.pos():
            self.setAllPositionChangeAccepted(True)
            self.setPos(position)
            self.setAllPositionChangeAccepted(False)

        # internal points
        self._point1 = self._pos1 - position
        self._point2 = self._pos2 - position
        self._rect = QRectF(self._point1, self._point2).normalized()

        self._shape_path = self.calculateShape(self._point1, self._point2)

        tip1_class = self._tip_class_from_tip_type[self._tip1]
        self._tip1_figure = tip1_class()
        self._tip1_figure.recalculate(self._point1, self._point2)
        tip2_class = self._tip_class_from_tip_type[self._tip2]
        self._tip2_figure = tip2_class()
        self._tip2_figure.recalculate(self._point2, self._point1)

        max_size = max(
            Settings.ELEMENT_PEN_SIZE,
            Settings.ELEMENT_SHAPE_SIZE,
            self._tip1_figure.tip_size,
            self._tip2_figure.tip_size,
        )

        extra = Settings.LINE_HANDLE_SIZE + max_size / 2
        self._bounding_rect = self._rect.adjusted(-extra, -extra, extra, extra)

        self.updateHandlePositions()

    def updateHandlePositions(self):
        self.setAllPositionChangeAccepted(True)

        if self._handler.handle[1].pos() != self._pos1:
            self._handler.handle[1].setPos(self._pos1)

        if self._handler.handle[2].pos() != self._pos2:
            self._handler.handle[2].setPos(self._pos2)

        self.setAllPositionChangeAccepted(False)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.ItemPositionChange:
            value = self.onItemPositionChange(value)
        if change == QGraphicsItem.ItemSceneChange:
            self.onItemSceneChange(value)
        if change == QGraphicsItem.ItemZValueHasChanged:
            self.onItemZValueHasChanged()
        if change == QGraphicsItem.ItemSelectedHasChanged:
            self.onItemSelectedHasChanged(value)
        return super().itemChange(change, value)

    def onItemPositionChange(self, position):
        if self.isPositionChangeAccepted():
            return position

        if QApplication.mouseButtons() == Qt.LeftButton:
            position = gui_utils.snap_position(position)

        if self.pos() == position:
            return position
        return self.calculateLinePositionChange(position)

    def calculateLinePositionChange(self, position):
        shift = position - self.pos()
        self._pos1 += shift
        self._pos2 += shift
        self.recalculate()
        return position

    def isPositionChangeAccepted(self) -> bool:
        return self._isPositionChangeAccepted

    def setPositionChangeAccepted(self, accepted: bool) -> None:
        self._isPositionChangeAccepted = accepted

    def onItemSceneChange(self, scene: QGraphicsScene):
        self._handler.on_scene_change(scene)

    def onItemZValueHasChanged(self):
        self._handler.on_zvalue_change()

    def onItemSelectedHasChanged(self, value):
        is_selected = bool(value)
        self.setLive(is_selected)

    def calculateHandlePositionChange(self, handle: LineHandleItem, position: QPointF):
        # This check simplifies dragging when line and both handles are selected
        if self.isSelected() and self._handler.countSelected() == 2:
            return position

        if handle == self._handler.handle[1]:
            self._pos1 = position

        if handle == self._handler.handle[2]:
            self._pos2 = position

        self.recalculate()
        return handle.pos()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def shape(self) -> QPainterPath:
        return self._shape_path

    def calculateShape(self, point1, point2):
        line = QLineF(point1, point2)
        angle = line.angle()
        line1 = QLineF.fromPolar(Settings.LINE_HALF_WIDTH, angle + 90).translated(
            point1
        )
        line2 = QLineF.fromPolar(Settings.LINE_HALF_WIDTH, angle - 90).translated(
            point1
        )
        line3 = QLineF.fromPolar(Settings.LINE_HALF_WIDTH, angle - 90).translated(
            point2
        )
        line4 = QLineF.fromPolar(Settings.LINE_HALF_WIDTH, angle + 90).translated(
            point2
        )

        path = QPainterPath()
        path.moveTo(line1.p2())
        path.lineTo(line2.p2())
        path.lineTo(line3.p2())
        path.lineTo(line4.p2())
        path.lineTo(line1.p2())
        return path

    _pen_style_from_line_type = {
        LineType.Solid: Qt.SolidLine,
        LineType.Dash: Qt.DashLine,
        LineType.Dot: Qt.DotLine,
    }

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None
    ) -> None:

        x1 = self._tip1_figure.point().x()
        y1 = self._tip1_figure.point().y()
        x2 = self._tip2_figure.point().x()
        y2 = self._tip2_figure.point().y()

        pen = (
            Settings.LINE_SELECTED_PEN
            if self.isSelected()
            else Settings.ELEMENT_NORMAL_PEN
        )

        line_pen = QPen(pen)
        line_pen_style = self._pen_style_from_line_type[self._line_type]
        line_pen.setStyle(line_pen_style)

        painter.setPen(line_pen)
        painter.drawLine(x1, y1, x2, y2)

        painter.setPen(pen)
        painter.setBrush(self._get_tip_brush(self._tip1))
        self._tip1_figure.paint(painter)

        painter.setBrush(self._get_tip_brush(self._tip2))
        self._tip2_figure.paint(painter)

        # pen = Settings.ELEMENT_SELECTED_PEN if self.isSelected() else Settings.ELEMENT_NORMAL_PEN
        # painter.setPen(pen)
        # painter.setBrush(Settings.ELEMENT_NORMAL_TRANSPARENT_BRUSH)
        # painter.drawRect(self.rect())
        #
        # painter.drawPath(self.shape())

    def _get_tip_brush(self, tip_type):
        if tip_type in [
            TipType.FullTriangle,
            TipType.FullDiamond,
            TipType.FullHalfTriangle,
        ]:
            brush = (
                Settings.LINE_SELECTED_BRUSH
                if self.isSelected()
                else Settings.ELEMENT_NORMAL_BRUSH
            )
        else:
            brush = (
                Settings.ELEMENT_SELECTED_TRANSPARENT_BRUSH
                if self.isSelected()
                else Settings.ELEMENT_NORMAL_TRANSPARENT_BRUSH
            )
        return brush

    def _handle_selection_changed(self, is_selected):
        self.setLive(is_selected)

    _tip_class_from_tip_type = {
        TipType.Empty: NoTip,
        TipType.Arrow: ArrowTip,
        TipType.HollowTriangle: TriangleTip,
        TipType.FullTriangle: TriangleTip,
        TipType.HollowDiamond: DiamondTip,
        TipType.FullDiamond: DiamondTip,
        TipType.FullHalfTriangle: HalfTriangleTip,
    }

    def _parse_text(self):
        """Parse

        Every line of text is either a command or a text for central label
        """
        label_lines = []
        lines = self.text().split("\n")
        for line in lines:
            if len(line) >= 4 and line[:3] == "lt=":
                self.set_line_type_from_text(line[3:])
            else:
                label_lines.append(line)
        self._label_text = "\n".join(label_lines)

    _tip_types = [
        TipType.Empty,
        TipType.Arrow,
        TipType.HollowTriangle,
        TipType.FullTriangle,
        TipType.HollowDiamond,
        TipType.FullDiamond,
        TipType.FullHalfTriangle,
    ]

    _tip1_type_from_txt = dict(
        zip(["", "<", "<<", "<<<", "<<<<", "<<<<<", "<<<<<<"], _tip_types)
    )
    _tip2_type_from_txt = dict(
        zip(["", ">", ">>", ">>>", ">>>>", ">>>>>", ">>>>>>"], _tip_types)
    )

    _lt_from_splitter = {
        "-": LineType.Solid,
        ".": LineType.Dash,
        "..": LineType.Dot,
    }

    def set_line_type_from_text(self, txt: str):
        """Parse line type"""

        if txt.find("-") >= 0:
            splitter = "-"
        elif txt.find("..") >= 0:
            splitter = ".."
        elif txt.find(".") >= 0:
            splitter = "."
        else:
            splitter = "-"

        self._line_type = self._lt_from_splitter[splitter]

        tips = txt.split(splitter)

        self._tip1 = TipType.Empty
        if len(tips) > 0:
            self._tip1 = self._tip1_type_from_txt.get(tips[0]) or TipType.Empty

        self._tip2 = TipType.Empty
        if len(tips) > 1:
            self._tip2 = self._tip2_type_from_txt.get(tips[1]) or TipType.Empty
