from PyQt6.QtWidgets import (
    QVBoxLayout,
    QPushButton,
    QFrame,
    QLabel,
)
from PyQt6.QtCore import (
    Qt,
    QTimer,
    QSize,
)
from PyQt6.QtGui import (
    QPalette,
    QColor,
)


STYLE = """
QWidget {
    font-size: 13px;
    color: white;
    background-color: #010814;
}
QFrame {
    border: 1px solid #424242;
    border-radius: 3px;
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 pink, stop: 0.4 #242424,
                                stop: 0.5 #2d2d33, stop: 1.0 pink);
}

QLabel {
    background: grey;
    color: white;
    border: none;
    opacity: 0.1;
}

QPushButton {
    padding: 2px 0px;
    color: #333;
    background-color: qradialgradient(cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,
                                    radius: 1.35, stop:0.5 pink, stop: 1 white);
    border-radius: 5px;
}

/* Comment out the following to see the changes on hover */
QPushButton:hover {
    background-color: pink;
}

QPushButton:pressed {
    background-color: grey;
}
QPushButton:checked {
    background-color: grey;
}
"""


class CtrlBtn(QPushButton):
    """" custom  base button """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedWidth(70)
        self.setIconSize(QSize(32, 32))


class HidingBtn(CtrlBtn):
    """" custom button that can hide/show """

    def __init__(self, *args, hide_timer=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.hide_timer = hide_timer

    def enterEvent(self, event):
        if self.hide_timer:
            self.hide_timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.hide_timer:
            self.hide_timer.start()
        super().leaveEvent(event)


class MainWindow(QFrame):
    """ video display window """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)  # so we can detect cursor move
        self.setMinimumSize(400, 200)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.main_layout = QVBoxLayout(self)

        self.hide_timer = QTimer()
        self.hide_timer.setInterval(3000)  # ms
        self.hide_timer.timeout.connect(self.hide_widgets)

        self.on_init_create()
        # start timer on startup
        self.hide_timer.start()

    def on_init_create(self):
        """ create widgets/buttons """
        self.info_label = QLabel("Info: 100% Complete")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setFixedHeight(40)
        # btns
        self.download_btn = HidingBtn("Download", hide_timer=self.hide_timer)
        # add to layout
        self.main_layout.addWidget(self.info_label, alignment=Qt.AlignmentFlag.AlignTop)
        side = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        self.main_layout.addWidget(self.download_btn, alignment=side)

    def hide_widgets(self):
        """ hide widgets/btns on inactivity """
        # stop timer while ctrls are hidden
        self.hide_timer.stop()

        self.download_btn.hide()
        self.info_label.hide()
        self.setCursor(Qt.CursorShape.BlankCursor)  # hide cursor

    def show_widgets(self):
        """ show widgets/btns """

        self.download_btn.show()
        self.info_label.show()
        self.setCursor(Qt.CursorShape.ArrowCursor)  # show cursor
        # start timer to hide
        self.hide_timer.start()

    def mouseMoveEvent(self, event):
        """ on mouse move events """
        self.show_widgets()

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """ on mouse press events """

        self.hide_timer.stop()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        self.show_widgets()

        super().mouseReleaseEvent(event)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    win = MainWindow()
    win.showMaximized()

    sys.exit(app.exec())
