# auto-resize widgets
from PyQt5.QtWidgets import QApplication, QWidget, QSizePolicy, QGridLayout, QPushButton, QMainWindow, QLabel
import sys


class Win(QWidget):
	def __init__(self):
		super().__init__()
		self.root_stylesheet = "QWidget {background-color: qlineargradient(x1: 0, x2: 1, stop: 0 white, stop: 1 black)}"
		self.button_stylesheet = "QPushButton {background-color: qlineargradient(x1: 0, x2: 1, stop: 0 black, stop: 1 white)}"
		self.setStyleSheet(self.root_stylesheet)
		values = ("1", "2", "3",
					"4", "5", "6",
					"7", "8", "9")
		positions = [(r, c) for r in range(3) for c in range(3)]
		GridLayout = QGridLayout()
		self.setLayout(GridLayout)
		for position, value in zip(positions, values):
			button = QPushButton(value)
			button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
			button.setStyleSheet(self.button_stylesheet)
			GridLayout.addWidget(button, *position)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	win = Win()
	win.show()
	sys.exit(app.exec())
	pass
