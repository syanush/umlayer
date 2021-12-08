import abc
import importlib
import json
from enum import Enum
from typing import Optional

import PySide6.QtWidgets
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QGraphicsItem

from . import Settings


class Abilities(Enum):
    EDITABLE_TEXT = 1


class BaseElement(QGraphicsItem):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def positionNotify(self, change):
        if self.scene() and change == QGraphicsItem.ItemPositionHasChanged:
            self.notify()

    def notify(self):
        if self.scene() is not None:
            self.scene().notify()

    def getAbilities(self):
        return self._abilities

    def textColor(self):
        return (
            Settings.ELEMENT_TEXT_SELECTED_COLOR
            if self.isSelected()
            else Settings.ELEMENT_TEXT_NORMAL_COLOR
        )

    def toJson(self):
        dto = self.toDto()
        json_dto = json.dumps(dto)
        return json_dto

    @abc.abstractmethod
    def toDto(self):
        dto = {}
        dto["class_name"] = self.__class__.__name__
        position = self.pos()
        dto["x"] = position.x()
        dto["y"] = position.y()
        dto["zValue"] = self.zValue()
        return dto

    @abc.abstractmethod
    def setFromDto(self, dto):
        if dto["class_name"] != self.__class__.__name__:
            raise ValueError("dto")
        self.setPos(QPointF(dto["x"], dto["y"]))
        self.setZValue(dto["zValue"])

    def clone(self):
        dto = self.toDto()
        element = self.__class__()
        element.setFromDto(dto)
        return element

    @staticmethod
    def fromJson(json_dto):
        dto = json.loads(json_dto)
        module_instance = importlib.import_module("umlayer.gui")
        class_name = dto["class_name"]
        element_class = getattr(module_instance, class_name)
        instance = element_class()
        instance.setFromDto(dto)
        return instance
