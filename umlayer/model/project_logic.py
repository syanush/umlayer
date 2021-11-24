from uuid import UUID

from . import ProjectStorage, Project, Folder, Diagram


class ProjectLogic:
    def __init__(self, storage: ProjectStorage):
        self.storage = storage
        self.new_project()

    def new_project(self):
        self.project = Project()
        root = Folder("Root")
        self.project.setRoot(root)
        self.project.add(Diagram("Diagram 1"), root.id)
        self.project.add(Diagram("Diagram 2"), root.id)
        self.project.setDirty(False)

    def clear_project(self):
        self.project = Project()
        self.project.setDirty(False)

    def get_project(self):
        return self.project

    def _add_element(self, element, parent_id):
        self.project.add(element, parent_id)

    def create_folder(self, parent_id):
        element = Folder("New folder")
        self._add_element(element, parent_id)
        return element

    def create_diagram(self, parent_id):
        element = Diagram("New diagram")
        self._add_element(element, parent_id)
        return element

    def delete_element(self, element_id: UUID):
        """Delete elements from model recursively"""
        if element_id == self.project.root.id:
            return
        self.project.remove(element_id)

    def save(self, filename: str):
        """Saves project data and settings to a file

        Throws exceptions in case of errors
        """

        if filename is None:
            raise ValueError('filename is None')

        self.storage.save(self.project.elements.values(), filename)
        self.project.setDirty(False)

    def load(self, filename: str):
        """Loads project data and settings from a file

        Throws exceptions in case of errors
        """

        elements: list = self.storage.load(filename)

        root = elements[0]
        self.project.setRoot(root)

        for element in elements:
            if element.id != root.id:
                self.project.add(element, element.parent_id)

        self.project.setDirty(False)
