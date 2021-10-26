from .folder import Folder
from .diagram import Diagram
from .project import Project


class ProjectLogic:
    def __init__(self):
        self.project = Project()
        f = Folder("Root")
        self.project.setRoot(f)

        self.project.add(Folder("1"), f.id)
        self.project.add(Folder("2"), f.id)
        self.project.add(Diagram("3"), f.id)

    def get_project(self):
        return self.project
