from PySide6.QtCore import QSortFilterProxyModel, QModelIndex

from . import ItemRoles


class TreeSortModel(QSortFilterProxyModel):
    def getItemType(self, index: QModelIndex):
        return self.sourceModel().data(index, role=ItemRoles.TypeRole)

    def lessThan(self, left: QModelIndex, right: QModelIndex):
        model = self.sourceModel()
        left_type_value = self.getItemType(left).value
        right_type_value = self.getItemType(right).value

        if left_type_value < right_type_value:
            return True
        if left_type_value > right_type_value:
            return False

        left_name = model.data(left, role=ItemRoles.NameRole)
        right_name = model.data(right, role=ItemRoles.NameRole)

        return left_name < right_name
