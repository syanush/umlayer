from PySide6.QtGui import QStandardItemModel, QStandardItem

from .. import model, adapters

# from . import itemize, StandardItem


class StandardItemModel(QStandardItemModel):
    """
    Item model

    All methods must be called with model index (not proxy index).
    """

    def __init__(self) -> None:
        super().__init__()
        self.setHorizontalHeaderLabels([""])

    def rootItem(self) -> adapters.StandardItem:
        return self.item(0)

    def initializeFromProject(self, project: model.Project) -> None:
        self.clear()
        root_item = adapters.itemize(project.root, project)
        self.appendRow([root_item])

    def count(self) -> int:
        root_model_index = self.rootItem().index()
        return 1 + self._countChildren(root_model_index)

    def _countChildren(self, model_index) -> int:
        count = row_count = self.rowCount(model_index)
        for i in range(row_count):
            child_model_index = self.index(i, 0, model_index)
            count += self._countChildren(child_model_index)
        return count
