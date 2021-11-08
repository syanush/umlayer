from PySide6.QtCore import *
from PySide6.QtGui import *

from .. import model


class StandardItemModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels([''])
        self.setSortRole(Qt.DisplayRole)

    @property
    def root_item(self):
        return self.item(0)

    def count(self):
        return 1 + self._countChildren(self.root_item.index())

    def _countChildren(self, index) -> int:
        count = rowCount = self.rowCount(index)
        for i in range(rowCount):
            count += self._countChildren(self.index(i, 0, index))
        return count

    @staticmethod
    def makeItem(element):
        element_type_to_icon_file = {
            model.Folder: 'resources/icons/folder.png',
            model.Diagram: 'resources/icons/diagram.png'
        }

        item = QStandardItem(element.name)
        item.setData(element.id, Qt.UserRole)
        element_type = type(element)
        item.setIcon(QIcon(element_type_to_icon_file[element_type]))
        return item

    @staticmethod
    def itemize(element, project):
        item = StandardItemModel.makeItem(element)

        children = project.children(element.id)
        for child in children:
            child_item = StandardItemModel.itemize(child, project)
            item.appendRow([child_item])
        return item
