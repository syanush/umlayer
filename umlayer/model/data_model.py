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

    def create_project(self) -> Project:
        self._project = Project()

    def delete_project(self) -> None:
        self._project = None

    @property
    def filename(self) -> str:
        return self._filename

    def set_filename(self, filename: str) -> None:
        self._filename = filename
