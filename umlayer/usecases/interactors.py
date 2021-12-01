from umlayer import model
from . import SaveInteractor

class Interactors:
    """
    Stores links to interactors for external users
    Sets external dependencies for interactors
    """

    def __init__(self,
                 data_model: model.DataModel,
                 save_interactor: SaveInteractor):

        self._data_model: model.DataModel = data_model
        self._save_interactor: SaveInteractor = save_interactor

    def set_window(self, window):
        self._save_interactor.set_window(window)

    @property
    def save_interactor(self) -> SaveInteractor:
        return self._save_interactor

    def create_project(self) -> model.Project:
        project = model.Project()
        self._data_model.set_project(project)

    def delete_project(self) -> None:
        self._data_model.set_project(None)

    def set_filename(self, filename):
        self._data_model.set_filename(filename)

    def delete_filename(self) -> None:
        self._data_model.set_filename(None)
