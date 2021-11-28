from uuid import UUID

from . import BaseItem

class Event:
    def __init__(self):
        self._handlers = []

    def subscribe(self, handler):
        self._handlers.append(handler)

    def unsubscribe(self, handler):
        index = self._handlers.index(handler)
        if index != -1:
            del self._handlers[index]

    def notify(self):
        for handler in self._handlers:
            handler()


class Project:
    def __init__(self):
        self.project_items = {}
        self.root = None
        self._is_dirty = False
        self._is_dirty_changed = Event()

    @property
    def isDirtyChangedEvent(self):
        return self._is_dirty_changed

    def dirty(self):
        return self._is_dirty

    def setDirty(self, dirty):
        if self._is_dirty == dirty:
            return

        self._is_dirty = dirty
        self.isDirtyChangedEvent.notify()

    def setRoot(self, root: BaseItem):
        self._add(root)
        self.root = root

    def remove(self, project_item_id: UUID = None):
        if project_item_id not in self.project_items.keys():
            raise AttributeError("element_id")
        self._remove(project_item_id)
        self.setDirty(True)

    def _remove(self, project_item_id: UUID = None):
        for child in self.children(project_item_id):
            self._remove(child.id)
        del self.project_items[project_item_id]

    def add(self, project_item: BaseItem, parent_id: UUID = None):
        if parent_id not in self.project_items.keys():
            raise AttributeError("parent_id")
        self._add(project_item, parent_id)
        self.setDirty(True)

    def _add(self, project_item: BaseItem, parent_id: UUID = None):
        project_item.parent_id = parent_id
        self.project_items[project_item.id] = project_item

    def get(self, project_item_id: UUID) -> BaseItem:
        return self.project_items.get(project_item_id)

    def children(self, parent_id: UUID) -> set[BaseItem]:
        return set(project_item for project_item in self.project_items.values()
                   if project_item.parent_id == parent_id)

    def count(self):
        return len(self.project_items)

    def printProjectItems(self):
        """Debugging feature"""
        for project_item in self.project_items.values():
            print(f'{project_item.name}   {project_item.id}')
        print()
