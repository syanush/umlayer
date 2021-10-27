from .folder import Folder
from .diagram import Diagram
from .project import Project


class ProjectLogic:
    def __init__(self):
        self.project = Project()
        root = Folder("Root")
        self.project.setRoot(root)

        self.project.add(Folder("1"), root.id)
        self.project.add(Folder("2"), root.id)
        self.project.add(Diagram("3"), root.id)

    def get_project(self):
        return self.project

    def create_folder(self, parent_id):
        element = Folder("New folder")
        self.project.add(element, parent_id)
        return element

    def create_diagram(self, parent_id):
        element = Diagram("New diagram")
        self.project.add(element, parent_id)
        return element

    def delete_element(self, element_id):
        self.project.remove(element_id)
