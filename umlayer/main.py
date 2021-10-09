import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from gui import app
from gui.mainwindow import MainWindow


def main():
    try:
        # print(PySide6.__version__)
        # print(PySide6.QtCore.__version__)
        myApp = QApplication(sys.argv)
        myWindow = MainWindow()
        myWindow.center()
        myApp.exec()
        sys.exit(0)
    except SystemExit:
        print("Closing MainWindow...")
    except Exception:
        print(sys.exc_info()[1])


if __name__ == '__main__':
    main()
