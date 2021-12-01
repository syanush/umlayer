from . import Project

class DataModel:
    """Entity. Application state. Holds links to the memory data: collections of other entities, etc

    Does not contain logic
    """
    def __init__(self) -> None:
        self._project: Project = None
        self._filename: str = None

    @property
    def project(self) -> Project:
        return self._project

    def set_project(self, project: Project) -> None:
        self._project = project

    @property
    def filename(self) -> str:
        return self._filename

    def set_filename(self, filename: str) -> None:
        self._filename = filename
