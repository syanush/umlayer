from PySide6.QtGui import QIcon, QStandardItem

from .. import model
from . import StandardItem

ITEM_TYPE_TO_ICON = {
    model.ProjectItemType.FOLDER: "icons:folder.png",
    model.ProjectItemType.DIAGRAM: "icons:diagram.png",
}


def itemize(project_item, project) -> StandardItem:
    item: StandardItem = makeItemFromProjectItem(project_item)
    children: set[model.BaseItem] = project.children(project_item.id)
    for child in children:
        child_item: StandardItem = itemize(child, project)
        item.appendRow([child_item])
    return item


def makeItemFromProjectItem(project_item: model.BaseItem) -> StandardItem:
    item_name = project_item.name()
    item_id = project_item.id
    item_type = project_item.item_type
    item: StandardItem = _makeItem(item_name, item_id, item_type)
    return item


def _makeItem(item_name, item_id, item_type) -> StandardItem:
    item = StandardItem()
    item.setText(item_name)
    item.setItemId(item_id)
    item.setItemType(item_type)
    icon_name = ITEM_TYPE_TO_ICON[item_type]
    item.setIcon(QIcon(icon_name))
    return item
