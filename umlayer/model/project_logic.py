from uuid import UUID

from . import ProjectStorage, Project, Folder, Diagram


class ProjectLogic:
    def __init__(self, storage: ProjectStorage):
        self._storage = storage
        self._project = None

    def init_new_project(self, project):
        self._project = project
        root = Folder("Root")
        self._project.setRoot(root)
        self._project.add(Diagram("Diagram 1"), root.id)
        self._project.setDirty(False)

    def get_project(self):
        return self._project

    def _add_project_item(self, element, parent_id):
        self._project.add(element, parent_id)

    def create_folder(self, parent_id):
        project_item = Folder("New folder")
        self._add_project_item(project_item, parent_id)
        return project_item

    def create_diagram(self, parent_id):
        project_item = Diagram("New diagram")
        self._add_project_item(project_item, parent_id)
        return project_item

    def delete_project_item(self, project_item_id: UUID):
        """Delete elements from model recursively"""
        if project_item_id == self._project.root.id:
            return
        self._project.remove(project_item_id)

    def save(self, filename: str):
        """Saves project data and settings to a file

        Throws exceptions in case of errors
        """

        if filename is None:
            raise ValueError('filename is None')

        project_items = self._project.project_items.values()
        self._storage.save(project_items, filename)
        self._project.setDirty(False)

    def storage_load(self, filename):
        return self._storage.load(filename)
