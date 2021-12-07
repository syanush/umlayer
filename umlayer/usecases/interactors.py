from umlayer import model
from . import ProjectInteractor


class Interactors:
    """
    Stores links to interactors for external users
    Sets external dependencies for interactors
    """

    def __init__(
        self, data_model: model.DataModel, project_interactor: ProjectInteractor
    ):

        self._data_model: model.DataModel = data_model
        self._project_interactor: ProjectInteractor = project_interactor

    def set_window(self, window):
        self._project_interactor.set_window(window)

    @property
    def project_interactor(self) -> ProjectInteractor:
        return self._project_interactor
