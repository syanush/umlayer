from umlayer import model
from . import SaveInteractor

class Interactors:
    def __init__(self,
                 data_model: model.DataModel,
                 save_interactor: SaveInteractor):

        self._data_model: model.DataModel = data_model
        self._save_interactor: SaveInteractor = save_interactor

    @property
    def data_model(self) -> model.DataModel:
        """
        TODO: Should not exist in the correct architecture.
        Interactors completely incapsulate the access to the data model.
        """
        return self._data_model

    def save_interactor(self) -> SaveInteractor:
        return self._save_interactor

    def create_project(self) -> model.Project:
        project = model.Project()
        self.data_model.set_project(project)

    def delete_project(self) -> None:
        self.data_model.set_project(None)

    def set_filename(self, filename):
        self.data_model.set_filename(filename)

    def delete_filename(self) -> None:
        self.data_model.set_filename(None)