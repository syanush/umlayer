from PySide6.QtWidgets import *


# Our main window class
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initGUI()

    def initGUI(self):
        self.setWindowTitle("UMLayer")
        self.show()
        print("Main window initialized.\n")

    def center(self):
        """ Function to center the main window
        """

        qRect = self.frameGeometry()
        centerPoint = self.screen().availableGeometry().center()
        qRect.moveCenter(centerPoint)
        self.move(qRect.topLeft())
