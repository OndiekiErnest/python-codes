from PyQt6.QtWidgets import (
    QApplication, QMainWindow,
)
from home import HomeWindow
from customs.qss import STYLE
import sys


class MainWin(QMainWindow):
    """ main app window """

    __slots__ = ("home", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Management")
        self.setMinimumSize(850, 500)

        self.home = HomeWindow()
        self.setCentralWidget(self.home)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    app.setStyle("Fusion")

    win = MainWin()
    win.showMaximized()

    sys.exit(app.exec())
