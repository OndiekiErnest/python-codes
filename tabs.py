from PyQt5.QtCore import Qt, QSize
from vtab import TabWidget
from PyQt5.QtGui import (
    QColor,
    QPalette,
    QIcon)
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QWidget)

class Color(QWidget):

    def __init__(self, color: str):
        super().__init__()
        self.setAutoFillBackground(1)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TABS")
        self.resize(300, 500)
        tabs = TabWidget()
        tabs.setMovable(1)
        icon = QIcon("C:\\Users\\code\\Pictures\\add_121935.png")
        with open("qtabwidget.css") as f:
            style = f.read()
            tabs.setStyleSheet(style)
        # tabs.setStyleSheet("""QTabBar::tab{padding: 40px;}
        #     QTabBar::tab:selected {
        #     background: white;
        #     }

        #     QTabBar::tab:!selected {
        #     background: silver;
        #     }
        #     QTabBar::tab {
        #     border: 1px solid white;}""")

        for color in ("red", "blue", "green", "pink"):
            tabs.addTab(Color(color), icon, color)
        tabs.setIconSize(QSize(50, 50))

        self.setCentralWidget(tabs)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
