from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QSizePolicy, QGridLayout, QFontDialog, QTabWidget
from PyQt5.QtGui import QFont
import sys

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("asfa")
        # self.resize(300, 500)
        book = QTabWidget()
        book.setTabPosition(QTabWidget.West)
        # button font
        self.button_font = QFont()
        self.button_font.setFamily("Helvetica")
        self.button_font.setPointSize(16)
        layout = QGridLayout()
        self.setLayout(layout)
        self.label = QLabel("HELLO", self)
        self.label.setStyleSheet("background: green; color: white")
        # self.label.setAlignment()
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button = QPushButton("CLICK", self)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button.setFont(self.button_font)
        # tip when cursor on the button
        button.setToolTip("Choose font")
        button.clicked.connect(self.show_fonts)
        # button.move(50, 0)
        layout.addWidget(self.label)
        layout.addWidget(button)
        # layout.removeWidget(self.label)

    def show_fonts(self):
        dialog = QFontDialog()
        dialog.setWindowTitle("Choose font")
        # modal mode blocks the main window, modeless doesn't
        # dialog.setWindowModality(Qt.ApplicationModal)
        # returns 1 if ok is clicked
        # dialog.exec_()
        self.setLabelFont(dialog.getFont()[0])

    def setLabelFont(self, font):
        self.label.setFont(font)
        self.button_font = font


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
