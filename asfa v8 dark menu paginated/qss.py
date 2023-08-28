disksTab = """
QTabBar::tab {
    padding-right: 3px;
    padding-left: 3px;
    color: black;
}
QTabBar::tab:selected {
    background-color: #ffffff;
}
QTabBar::tab:!selected {
    background-color: #5bc0eb;
}
QTabBar::tab:!selected:hover {
    border: 1px solid #f7fffe;
}
"""

# main styling
QSS = """
.QPushButton {
    background-color: #5bc0eb;
    color: black;
}
.QPushButton:hover {
    border: 2px solid #f7fffe;
    border-radius: 5px;
}
.QPushButton:enabled {
    color: black;
}
.QPushButton:disabled {
    color: gray;
}
QWidget#mainWindow {
    background-color: #211a1e;
    color: #ffffff;
}
QWidget {
    font: 16px;
    color: #ffffff;
}
QTabWidget::pane {
    border: 1px solid #211a1e;
    top: -1px;
    background-color: #211a1e;
}
QTabBar::tab {
    border: 1px solid #211a1e;
    padding: 0px 25px;
    color: black;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    border-top: 10px solid #ffffff;
    border-bottom: 10px solid #ffffff;
    margin-bottom: -1px;
}
QTabBar::tab:!selected {
    background-color: #5bc0eb;
}
QTabBar::tab:!selected:hover {
    border: 2px solid #f7fffe;
}
QLineEdit {
    background-color: #282828;
    color: #ffffff;
}
QLineEdit#searchInput {
    background-color: #353535;
}
QLineEdit:read-only, QLineEdit:focus:read-only {
    background-color: #211a1e;
    color: #ffffff;
    border: 1px solid gray;
}
QLineEdit:focus, QLineEdit#searchInput:focus {
    border: 1px solid #5bc0eb;
}
QSpinBox {
    background-color: #282828;
    color: #ffffff;
}
QComboBox {
    background-color: #5bc0eb;
    color: black;
}
QTableView {
    background-color: #282828;
    alternate-background-color: #353535;
    color: #ffffff;
}
QTableView:!focus {
    alternate-background-color: #353535;
}
QHeaderView {
    background-color: #5bc0eb;
    color: black;
}
/* QHeaderView::section:hover {
    background-color: #5bc0eb;
    border: 1px solid #f7fffe;
} */
QMenu {
    background-color: #282828;
    color: #ffffff;
}
QMenu::item {
    background-color: #353535;
    color: #ffffff;
}
QMenu::item:selected {
    border: 2px solid #f7fffe;
}
QScrollBar {
    background-color: #282828;
}
QScrollBar::handle {
    background-color: #353535;
}
QScrollBar::handle:hover {
    background-color: gray;
}
"""
