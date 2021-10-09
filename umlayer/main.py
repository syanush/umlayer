import sys

from gui.app import UMLayerApplication
from gui.mainwindow import MainWindow


def run_application():
    """Construct and run the UMLayer application
    """

    app = UMLayerApplication(sys.argv)
    main_window = MainWindow()
    main_window.center()
    app.setActiveWindow(main_window)
    result_code = app.exec()
    main_window = None
    app = None
    return result_code


def main():
    """Start function
    """

    try:
        errcode = run_application()
    except SystemExit:
        errcode = 0
    except Exception:
        print(sys.exc_info()[1])
        errcode = 1

    sys.exit(errcode)


if __name__ == '__main__':
    main()
