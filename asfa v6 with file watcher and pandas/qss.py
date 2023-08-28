
dark_background_color = "#4d4d4d"

QSS = """
QWidget {
    background: #262626;
    color: white
}

QLabel {
    background: #4d4d4d;
    font: 14px;
    height: 26px;
}

QListWidget {
    border: 0px
}

QPushButton {
    font: 14px Arial;
    background: #4d4d4d;
    height: 19px;
}

QPushButton:!selected:hover {
    background: #999;
}

QLineEdit {
    border: 1px solid #1f7d02;
    background: #4d4d4d;
    height: 26px;
    color: white;
    font: 12px
}

QListWidget {
    font: 13px Arial;
    color: #efefef;
}
QTabWidget {
    padding: 30px 15px 30px 15px;
}

QTabWidget::tab-bar:top {
    top: 1px;
}

QTabWidget::tab-bar:bottom {
    bottom: 1px;
}

QTabWidget::tab-bar:left {
    right: 1px;
}

QTabWidget::tab-bar:right {
    left: 1px;
}

QTabBar::tab {
    border: 1px solid black;
}

QTabBar::tab:selected {
    background: #1f7d02;
}

QTabBar::tab:!selected {
    background: #4d4d4d;
}

QTabBar::tab:!selected:hover {
    background: #999;
}

QTabBar::tab:top:!selected {
    margin-top: 3px;
}

QTabBar::tab:bottom:!selected {
    margin-bottom: 3px;
}

QTabBar::tab:top, QTabBar::tab:bottom {
    min-width: 8ex;
    margin-right: -1px;
    padding: 5px 10px 5px 10px;
}

QTabBar::tab:top:selected {
    border-bottom-color: none;
}

QTabBar::tab:bottom:!selected {
    border-top-color: none;
}

QTabBar::tab:top:last, QTabBar::tab:bottom:last,
QTabBar::tab:top:only-one, QTabBar::tab:bottom:only-one {
    margin-right: 0;
}

QTabBar::tab:left:!selected {
    margin-right: 3px;
}

QTabBar::tab:right:!selected {
    margin-left: 3px;
}

QTabBar::tab:left, QTabBar::tab:right {
    min-height: 8ex;
    margin-bottom: -1px;
    padding: 10px;
}

QTabBar::tab:left:selected {
    border-left-color: none;
}

QTabBar::tab:right:selected {
    border-right-color: none;
}

QTabBar::tab:left:last, QTabBar::tab:right:last,
QTabBar::tab:left:only-one, QTabBar::tab:right:only-one {
    margin-bottom: 0;
}
"""
