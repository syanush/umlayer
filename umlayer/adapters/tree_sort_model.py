from PySide6.QtCore import QModelIndex, QSortFilterProxyModel

from umlayer.adapters import StandardItem, StandardItemModel


class TreeSortModel(QSortFilterProxyModel):
    def lessThan(self, left: QModelIndex, right: QModelIndex):
        model: StandardItemModel = self.sourceModel()
        left_item: StandardItem = model.itemFromIndex(left)
        right_item: StandardItem = model.itemFromIndex(right)

        left_type_value = left_item.itemType().value
        right_type_value = right_item.itemType().value

        if left_type_value < right_type_value:
            return True
        if left_type_value > right_type_value:
            return False

        return left_item.itemName() < right_item.itemName()
