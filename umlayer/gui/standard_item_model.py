from PySide6.QtCore import *
from PySide6.QtGui import *

import model


class StandardItemModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels([''])
        self.setSortRole(Qt.DisplayRole)
        self._root_item = None

    def root_item(self):
        return self._root_item  # self.item(0)

    def updateItemModel(self, project):
        self._root_item = self.itemize(project.root, project)
        self.appendRow([self._root_item])

    def count(self):
        return 1 + self._countChildren(self.root_item().index())

    def _countChildren(self, index) -> int:
        count = rowCount = self.rowCount(index)
        for i in range(rowCount):
            count += self._countChildren(self.index(i, 0, index))
        return count

    @staticmethod
    def makeItem(project_item: model.BaseItem):
        project_item_type_to_icon_file = {
            model.Folder: model.icon_path('folder.png'),
            model.Diagram: model.icon_path('diagram.png')
        }

        item = QStandardItem(project_item.name())
        item.setData(project_item.id, Qt.UserRole)
        element_type = type(project_item)
        item.setIcon(QIcon(project_item_type_to_icon_file[element_type]))
        return item

    @staticmethod
    def itemize(element, project):
        item = StandardItemModel.makeItem(element)

        children = project.children(element.id)
        for child in children:
            child_item = StandardItemModel.itemize(child, project)
            item.appendRow([child_item])
        return item
