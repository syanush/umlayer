from uuid import UUID

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem

from umlayer import model


class ItemRoles:
    NameRole = Qt.DisplayRole
    IdRole = Qt.UserRole
    TypeRole = Qt.UserRole + 1


class StandardItem(QStandardItem):
    def itemId(self) -> UUID:
        return self.data(ItemRoles.IdRole)

    def setItemId(self, item_id: UUID) -> None:
        self.setData(item_id, ItemRoles.IdRole)

    def itemType(self) -> model.ProjectItemType:
        return self.data(ItemRoles.TypeRole)

    def setItemType(self, item_type: model.ProjectItemType) -> None:
        self.setData(item_type, ItemRoles.TypeRole)

    def itemName(self) -> str:
        return self.data(ItemRoles.NameRole)
