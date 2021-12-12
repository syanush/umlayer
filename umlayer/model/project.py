from uuid import UUID

from . import BaseItem


class Project:
    """Contains project data"""

    def __init__(self):
        self.project_items = {}  # bad design
        self._root = None
        self._is_dirty = False

    @property
    def root(self):
        return self._root

    def setRoot(self, root: BaseItem):
        self._add(root)
        self._root = root

    def __str__(self):
        return f"<Project root={self._root}>"

    def dirty(self):
        return self._is_dirty

    def setProjectDirty(self, dirty):  # bad design
        if self._is_dirty == dirty:
            return

        self._is_dirty = dirty

    def remove(self, project_item_id: UUID = None):
        if project_item_id not in self.project_items.keys():
            raise AttributeError("element_id")
        self._remove(project_item_id)
        self.setProjectDirty(True)

    def _remove(self, project_item_id: UUID = None):
        for child in self.children(project_item_id):
            self._remove(child.id)
        del self.project_items[project_item_id]

    def add(self, project_item: BaseItem, parent_id: UUID):
        if parent_id not in self.project_items:
            print(f"Add: item {parent_id} does not belong to {self}")
            self.printProjectItems()
            raise AttributeError("parent_id")
        self._add(project_item, parent_id)
        self.setProjectDirty(True)

    def _add(self, project_item: BaseItem, parent_id: UUID = None):
        project_item.parent_id = parent_id
        self.project_items[project_item.id] = project_item

    def get(self, project_item_id: UUID) -> BaseItem:
        return self.project_items.get(project_item_id)

    def children(self, parent_id: UUID) -> set[BaseItem]:
        return set(
            project_item
            for project_item in self.project_items.values()
            if project_item.parent_id == parent_id
        )

    def count(self):
        return len(self.project_items)

    def printProjectItems(self):
        """Debugging feature"""
        print(self)
        for item_id, project_item in self.project_items.items():
            print(
                f"{project_item.name():15s} id={project_item.id} par={project_item.parent_id}"
            )
            if item_id != project_item.id:
                print("Bad item")
        print()
