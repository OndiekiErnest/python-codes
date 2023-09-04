STYLE = """
QWidget {
    font-family: Consolas;
    font-size: 18px;
}
QTableView {
    border: 0px;
}
QGroupBox#innerGroup {
    border: 1px solid #a7a7a7;
    border-left: 0px;
    border-right: 0px;
    border-bottom: 0px;
    border-radius: 5px;
    margin-top: 4ex;
}
QGroupBox#innerGroup::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    background-color: white;
}
QGroupBox {
    border: 1px solid #a7a7a7;
    border-left: 0px;
    border-right: 0px;
    border-bottom: 0px;
    border-radius: 5px;
    margin-top: 4ex;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffffff, stop: 1 #e1e1e1);
}
QTabBar::tab {
    border: 1px solid #a7a7a7;
    padding: 0px 25px;
}
QTabBar::tab:selected {
    background-color: #ffffff;
    border-top: 10px solid #ffffff;
    border-bottom: 10px solid #ffffff;
    border-left: 0px;
    border-right: 0px;
    margin-bottom: -1px;
    font-weight: 900;
}
QTabBar::tab:!selected {
    background-color: #f0f0f0;
}
QTabBar::tab:!selected:hover {
    border: 2px solid #a7a7a7;
}
QLineEdit:read-only, QLineEdit:read-only:focus {
    background-color: #e3e3e3;
    border: solid #e3e3e3;
    /* border - top right bottom left */
    border-width: 1px;
    border-radius: 2px;
}
"""
