from PySide6.QtWidgets import *


class MainWindow(QWidget):
    """Main window of the UMLayer application
    """

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

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            'Window Close',
            'Are you sure you want to close the window?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            print('Main window closed.')
        else:
            event.ignore()
