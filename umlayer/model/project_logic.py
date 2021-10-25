from .folder import Folder
from .project import Project


class ProjectLogic:
    def __init__(self):
        self.project = Project()
        f = Folder("Root")
        self.project.setRoot(f)

        # i1 = Folder("Some")
        # self.project.add(i1, f.id)

    def get_project(self):
        return self.project
