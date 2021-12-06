from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem
from umlayer import model
from . import ItemRoles


class StandardItemModel(QStandardItemModel):
    """
    Item model

    All methods must be called with model index (not proxy index).
    """
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels([''])

    def root_item(self):
        return self.item(0)

    def initializeFromProject(self, project):
        self.clear()
        root_item = self.itemize(project.root, project)
        self.appendRow([root_item])

    def count(self):
        root_model_index = self.root_item().index()
        return 1 + self._countChildren(root_model_index)

    def _countChildren(self, model_index) -> int:
        count = rowCount = self.rowCount(model_index)
        for i in range(rowCount):
            count += self._countChildren(self.index(i, 0, model_index))
        return count

    _item_type_to_icon = {
        model.ProjectItemType.FOLDER: 'icons:folder.png',
        model.ProjectItemType.DIAGRAM: 'icons:diagram.png',
    }

    def makeItem(self, project_item: model.BaseItem) -> QStandardItem:
        item_type = project_item.item_type
        item = QStandardItem(project_item.name())
        item.setData(project_item.id, ItemRoles.IdRole)
        item.setData(item_type, ItemRoles.TypeRole)
        icon_name = self._item_type_to_icon[item_type]
        item.setIcon(QIcon(icon_name))
        return item

    def itemize(self, project_item, project):
        item = self.makeItem(project_item)
        children = project.children(project_item.id)
        for child in children:
            child_item = self.itemize(child, project)
            item.appendRow([child_item])
        return item
