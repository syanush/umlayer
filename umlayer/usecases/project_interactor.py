import logging
import traceback

from umlayer import model
from .project_storage import ProjectStorage


class ProjectInteractor:
    """Project operations"""

    def __init__(self, data_model: model.DataModel, storage: ProjectStorage):
        self._data_model = data_model
        self._storage: ProjectStorage = storage
        self._window = None

    @property
    def _project(self) -> model.Project:
        return self._data_model.project

    @property
    def _filename(self) -> str:
        return self._data_model.filename

    def set_window(self, window) -> None:
        self._window = window

    def is_project_open(self):
        return self._project is not None

    def is_dirty(self) -> bool:
        if not self.is_project_open():
            return False
        return self._project.dirty()

    def set_dirty(self, dirty: bool) -> None:
        if self.is_project_open():
            self._project.setProjectDirty(dirty)
        self._window.updateTitle()

    def set_project_item_name(self, id, name):
        if not self.is_project_open():
            return

        project_item = self._project.get(id)
        if project_item.name() != name:
            project_item.setName(name)
            self.set_dirty(True)

    def create_new_project(self):
        """Close old and create new project"""
        if not self.close_project():
            return

        self._do_create_new_project()

    def open_project(self) -> None:
        """Shows dialog for path to project file and opens project"""
        if not self.close_project():
            return

        filename = self._window.getFileNameFromOpenDialog("Open")

        if len(filename) == 0:
            return

        try:
            # raise Exception  # for debugging
            self._do_open_project(filename)
        except Exception as ex:
            logging.error(ex)
            print(ex)
            self._window.showCriticalError("Unable to open project!")
        else:
            self._data_model.set_filename(filename)
            self._window.updateTitle()

    def save_project(self) -> bool:
        """Saves project. Shows dialog for selecting file name, if it is not set."""
        if not self.is_project_open():
            return True

        if self._is_filename_unset():
            filename = self._window.getFileNameFromSaveDialog("Save")
        else:
            filename = self._filename

        if len(filename) == 0:
            return False

        return self._save_project_as_filename(filename)

    def save_project_as(self) -> None:
        if not self.is_project_open():
            return

        filename = self._window.getFileNameFromSaveDialog("Save as...")

        if len(filename) == 0:
            return

        self._save_project_as_filename(filename)

    def close_project(self) -> bool:
        """
        Tries to close project.

        Returns True if the project was closed successfully, False otherwise
        """
        if not self.save_project_if_needed():
            return False

        self._window.clearProjectTree()
        self._window.disableScene()

        self._data_model.delete_project()
        self._data_model.set_filename(None)

        self._window.updateTitle()
        return True

    def save_project_if_needed(self) -> bool:
        """Asks about saving modified project, and save it if needed

        Returns True if the project was saved successfully
        """
        if not self.is_dirty():
            return True

        reply = self._window.askToSaveModifiedProject()

        if reply == model.constants.SAVE:
            if not self.save_project():
                return False

        return reply != model.constants.CANCEL

    def _is_filename_unset(self) -> bool:
        return (
            self._filename is None or self._filename == model.constants.DEFAULT_FILENAME
        )

    def _save_project_as_filename(self, filename):
        try:
            self._do_save_project(filename)
            self._data_model.set_filename(filename)
            self._window.updateTitle()
            return True
        except Exception:
            logging.exception(traceback.format_exc())
            self._window.showCriticalError("Unable to save project!")
            return False

    def _do_save_project(self, filename) -> None:
        """Actually saves the project"""

        self._window.storeScene()
        self._save(filename)

    def _save(self, filename: str) -> None:
        """Saves project data and settings to a file

        Throws exceptions in case of errors
        """

        if filename is None:
            raise ValueError("filename")

        project_items = self._project.project_items.values()
        self._storage.save(project_items, filename)
        self.set_dirty(False)

    def _initializeTreeViewFromProject(self):
        self._window.initializeTreeFromProject()
        self.set_dirty(False)

    def _do_open_project(self, filename) -> None:
        self._load(filename)
        self._initializeTreeViewFromProject()

    def _load(self, filename: str) -> None:
        """Loads project data and settings from a file

        Throws exceptions in case of errors
        """

        project_items: list[model.BaseItem] = self._storage.load(filename)
        root = project_items[0]  # breadth first

        self._data_model.create_project()
        self._project.setRoot(root)

        for project_item in project_items:
            if project_item.id != root.id:
                self._project.add(project_item, project_item.parent_id)

        self.set_dirty(False)

    def _do_create_new_project(self) -> None:
        """Create new project with default content"""
        self._data_model.create_project()
        root = model.Folder("Root")
        self._project.setRoot(root)
        self._project.add(model.Diagram("Diagram 1"), root.id)
        self.set_dirty(False)
        self._set_default_file_name()
        self._window.updateTitle()
        self._initializeTreeViewFromProject()

    def _set_default_file_name(self) -> None:
        self._data_model.set_filename(model.constants.DEFAULT_FILENAME)
