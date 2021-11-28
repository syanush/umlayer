import os
import logging

from PySide6.QtCore import *
from PySide6.QtWidgets import *

import umlayer


class UMLayerApplication(QApplication):
    """UMLayer application class.

    It stores settings and other application resources
    """

    def __init__(self, args):
        super().__init__(args)

        QCoreApplication.setOrganizationName("SpiralArms")
        QCoreApplication.setOrganizationDomain("spiralarms.org")
        QCoreApplication.setApplicationName("UMLayer")

        # So that we can write: QIcon('icons:icon1.png')
        QDir.addSearchPath('icons', os.path.join(umlayer.__path__[0], 'resources', 'icons'))

        logging.info("Application constructor finished")
