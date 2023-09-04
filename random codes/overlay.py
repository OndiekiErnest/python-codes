from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtCore import QPoint, QRect, Qt, QObject, QEvent
from PyQt6.QtWidgets import QWidget, QApplication, QHBoxLayout, QLabel
import sys


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(30, 30, 600, 400)
        self.begin = QPoint()
        self.end = QPoint()
        self.show()

    def paintEvent(self, event):
        qp = QPainter(self)
        br = QBrush(QColor(100, 10, 10, 40))
        qp.setBrush(br)
        qp.drawRect(QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(30, 30, 600, 400)
        self.begin = QPoint()
        self.end = QPoint()

    def paintEvent(self, event):
        qp = QPainter(self)
        br = QBrush(QColor(100, 10, 10, 40))
        qp.setBrush(br)
        qp.drawRect(QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        print(self.begin, self.end)
        self.begin = event.pos()
        self.end = event.pos()
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec())
