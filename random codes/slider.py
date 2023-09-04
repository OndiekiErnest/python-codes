from PyQt5.QtWidgets import QSlider, QApplication, QMainWindow
from PyQt5.QtCore import Qt

SLIDER_STYLE = """
QSlider::groove:horizontal {
    background: white;
    height: 5px
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #66e, stop: 1 #bbf);
    background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1, stop: 0 #bbf, stop: 1 #55f);
    height: 5px
}
QSlider::add-page:horizontal {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:0.5 #fff, stop: 1 #d4d4d4);
    height: 5px
}
QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #52307c, stop: 1 #ece6ff);
    width: 13px;
    margin-top: -2px;
    margin-bottom: -2px;
    border-radius: 4px
}
QSlider::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #bca0dc, stop:1 #e0d6ff)
}
QSlider::sub-page:horizontal:disabled {
    background: #bbb;
    border-color: #999
}
QSlider::add-page:horizontal:disabled {
    background: #eee;
    border-color: #999
}
QSlider::handle:horizontal:disabled {
    background: #eee;
    border: 1px solid #aaa;
    border-radius: 4px
}
"""


class Main(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slider = QSlider()
        self.slider.setEnabled(True)
        self.slider.setMouseTracking(True)
        self.slider.setStyleSheet(SLIDER_STYLE)
        self.slider.setPageStep(10)
        self.slider.setSliderPosition(0)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setInvertedControls(False)
        self.setCentralWidget(self.slider)
        self.show()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = Main()
    sys.exit(app.exec())
