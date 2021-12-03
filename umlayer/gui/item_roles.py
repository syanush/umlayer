from enum import Enum

from PySide6.QtCore import *
from PySide6.QtGui import *


class ItemRoles:
    NameRole = Qt.DisplayRole
    IdRole = Qt.UserRole
    TypeRole = Qt.UserRole + 1
