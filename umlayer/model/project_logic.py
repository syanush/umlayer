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
        folder = Folder("New folder")
        self.project.add(folder, parent_id)
        return folder
