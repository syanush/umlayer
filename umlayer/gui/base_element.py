import abc
import importlib
import json
from enum import Enum

from PySide6.QtCore import *
from PySide6.QtWidgets import *


class Abilities(Enum):
    EDITABLE_TEXT = 1


class BaseElement(object):
    def __init__(self):
        self.notify = lambda: None

    def positionNotify(self, change):
        if self.scene() and change == QGraphicsItem.ItemPositionHasChanged:
            self.notify()

    def setNotify(self, notify):
        self.notify = notify

    def getAbilities(self):
        return self._abilities

    def toJson(self):
        dto = self.toDto()
        json_dto = json.dumps(dto)
        return json_dto

    @abc.abstractmethod
    def toDto(self):
        dto = {}
        dto['class_name'] = self.__class__.__name__
        position = self.pos()
        dto['x'] = position.x()
        dto['y'] = position.y()
        return dto

    @abc.abstractmethod
    def setFromDto(self, dto):
        if dto['class_name'] != self.__class__.__name__:
            raise ValueError('dto')
        self.setPos(QPointF(dto['x'], dto['y']))

    @staticmethod
    def fromJson(json_dto):
        dto = json.loads(json_dto)
        module_instance = importlib.import_module('umlayer.gui')
        class_name = dto['class_name']
        element_class = getattr(module_instance, class_name)
        instance = element_class()
        instance.setFromDto(dto)
        return instance
