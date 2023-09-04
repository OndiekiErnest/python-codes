""" custom style for media player """

STYLE = """
QWidget {
    font-size: 15px;
    font-family: Consolas;
    color: white;
    background-color: #010814;
}
QFrame {
    border: 1px solid #424242;
    border-radius: 3px;
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #1f1f21, stop: 0.4 #242424,
                                stop: 0.5 #2d2d33, stop: 1.0 #1f1f21);
}

QLabel {
    background: rgba(12, 12, 233, 0.02);
    color: rgba(255, 255, 255, 0.9);
    border: none;
    opacity: 0.1;
}

QListView {
    background-color: rgba(12, 12, 233, 0.02);
    border: none;
}

QToolTip {
    background-color: white;
    color: rgba(0, 0, 0, 0.9);
    border: 1px solid black;
}

QPushButton {
    padding: 2px 0px;
    color: #333;
    background-color: qradialgradient(cx: 0.3, cy: -0.4, fx: 0.3, fy: -0.4,
                                    radius: 1.35, stop:0.5 #02c0f5, stop: 1 #d4d4d4);
    border-radius: 5px;
}

QPushButton:hover {
    background-color: #37cffa;
}

QPushButton:pressed {
    background-color: #049cc7;
}
QPushButton:checked {
    background-color: #03a9fc;
}

QSlider {
    background-color: #242424;
    color: white;
}

QSlider::groove:horizontal {
    height: 5px;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background-color: #02c0f5;
    height: 5px;
}

QSlider::add-page:horizontal {
    background-color: #d4d4d4;
    height: 5px;
}

QSlider::handle:horizontal {
    background-color: #03a5fc;
    width: 7px;
    height: 5px;
    line-height: 10px;
    margin-top: -3px;
    margin-bottom: -3px;
    border: 2px solid #03a5fc;
    border-radius: 5px;
}

QSlider::sub-page:horizontal:disabled {
    background-color: #bbb;
    border-color: #999;
}

QSlider::add-page:horizontal:disabled {
    background-color: #eee;
    border-color: #999;
}

QSlider::handle:horizontal:disabled {
    background-color: #eee;
    border: 1px solid #aaa;
    border-radius: 4px;
}
"""
