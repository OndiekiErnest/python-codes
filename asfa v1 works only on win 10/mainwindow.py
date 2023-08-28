__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"

import time
from os import path
from qss import QSS
from PyQt5.QtCore import Qt, QSize, QRect, QPoint, QThreadPool
from PyQt5.QtGui import (
    QColor,
    QPalette,
    QIcon,
    QFont)
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QWidget,
    QStyle,
    QTabBar,
    QStylePainter,
    QStyleOptionTab,
    QTabWidget,
    QFrame,
    QVBoxLayout, QHBoxLayout,
    QGridLayout,
    QSizePolicy,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QComboBox,
    QScrollArea,
    QCheckBox,
    QMessageBox)

ListWidgetItem = QListWidgetItem
qt = Qt
threadpool = QThreadPool


class DownloadDialog(QFrame):
    """
        create a window to hold a label, a button and able to destroy itself
    """

    def __init__(self, labeltxt, buttontxt):
        super().__init__()
        line = Line()
        self.label = QLabel()
        # self.label.setStyleSheet("background: #262626")
        self.button = QPushButton()
        self.update_w(labeltxt, buttontxt)
        self.layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.label)
        hlayout.addStretch()
        hlayout.addWidget(self.button)
        self.layout.addLayout(hlayout)
        self.layout.addWidget(line)
        self.setLayout(self.layout)

    def close(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                widget = child.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.close(child.layout())

    def update_w(self, labeltxt, buttontxt):
        self.label.setText(labeltxt)
        self.button.setText(buttontxt)
        if buttontxt == "Open":
            # link button to open_files function
            pass
        else:
            self.button.clicked.connect(lambda: self.close(self.layout))


# ---------------------- CUSTOM LINE -------------------------------------------------------
class Line(QFrame):
    def __init__(self, h=1):
        super().__init__()
        if h:
            # defaults to horizontal line
            self.setFrameShape(QFrame.HLine)
        else:
            self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
        # self.setStyleSheet("background: #999")
# ---------------------- END CUSTOM LINE -------------------------------------------------------
class MessageBox(QFrame):

    """
        create a msg box for texts and files
    """

    def __init__(self, msg=None, file=None, reply=None):
        super().__init__()
        self.msg, self.file, self.reply = msg, file, reply
        self.color = "#4891da"
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("margin: 0px; background: #4891da; color: white")
        self.font = self.font()
        self.font.setPointSize(12)
        self.setFont(self.font)
        self.setFixedHeight(40)
        self.create()

    def create(self):
        self.download_check_button = QCheckBox(self.msg, self)
        self.download_check_button.setFont(self.font)
        self.size_label = QLabel("34.2 MB", self)
        self.size_label.setFont(self.font)
        self.date_modified_label = QLabel("26/03/2019", self)
        self.date_modified_label.setFont(self.font)
        self.layout.addWidget(self.download_check_button)
        self.layout.addWidget(self.date_modified_label)
        self.layout.addWidget(self.size_label)


# ------------------------------------ CUSTOM TAB WIDGET ------------------------------------------
class TabBar(QTabBar):
    """
        create vertical tabs with horizontal texts
    """

    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            # s = QSize(200, 300)
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            # set the font
            font = painter.font()
            font.setPointSize(14)
            painter.setFont(font)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()


class TabWidget(QTabWidget):
    """
        create vertical tabs with horizontal icons and texts
    """

    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))
        self.setTabPosition(QTabWidget.West)
# --------------------------------------------- END OF CUSTOM TAB WIDGET ---------------------------------


class DiskMan():
    """
        disk window manager
    """

    def __init__(self):
        # window icons
        self.copy_icon = QIcon("data\\copy.png")
        self.cut_icon = QIcon("data\\cut.png")
        self.delete_icon = QIcon("data\\delete.png")
        self.open_icon = QIcon("data\\open.png")
        self.disk_management_win = QWidget()
        self.main_layout = QVBoxLayout()
        # self.main_layout = None

    def create_disk_win(self):
        """
            create the window to hold widgets
            that will go in the disk management tab
        """

        self.close(self.main_layout)
        hlayout = QHBoxLayout()
        # use v layout for this widget
        self.disk_management_win.setLayout(self.main_layout)
        # select between multiple external disks
        self.dropdown_menu = QComboBox()
        self.dropdown_menu.setInsertPolicy(QComboBox.NoInsert)
        self.dropdown_menu.setFixedSize(200, 33)
        # create the control buttons
        self.copy_button = QPushButton("Copy")
        self.copy_button.setIcon(self.copy_icon)
        # self.copy_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cut_button = QPushButton("Cut")
        self.cut_button.setIcon(self.cut_icon)
        self.open_button = QPushButton("Open")
        self.open_button.setIcon(self.open_icon)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setIcon(self.delete_icon)
        self.select_all_button = QPushButton("Select All")
        # add to the top in a horizontal manner
        hlayout.addWidget(self.dropdown_menu)
        hlayout.addWidget(self.copy_button)
        hlayout.addWidget(self.cut_button)
        hlayout.addWidget(self.open_button)
        hlayout.addWidget(self.delete_button)
        hlayout.addWidget(self.select_all_button)
        hlayout.addStretch()
        # create search area
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files in current folder")
        self.search_button = QPushButton("Search")
        hlayout.addWidget(self.search_input)
        hlayout.addWidget(self.search_button)
        # nest an inner layout
        self.main_layout.addLayout(hlayout)
        # create the inner vertical tab widget
        self.folders_tab = TabWidget()
        self.folders_tab.setMovable(1)
        self.folders_tab.setDocumentMode(1)
        # self.folders_tab.setStyleSheet("QTabBar::tab {height: 50px; width: 20px}")
        # add this tab to the vertical layout
        self.main_layout.addWidget(self.folders_tab)
        # add this window to the tab
        # self.create_files_list()

    def create_files_list(self, items: tuple):
        """
            create a table to show files in different folders
        """

        self.list_widget = QListWidget()
        self.list_widget.setSortingEnabled(1)
        self.list_widget.setSpacing(4)
        self.list_widget.setFrameStyle(0)
        font = self.list_widget.font()
        font.setPointSize(12)
        self.list_widget.setFont(font)
        # add items TODO: add a loop here
        for item in items[1]:
            QListWidgetItem(item, self.list_widget).setCheckState(Qt.Unchecked)
        # add the list view to the tab
        folder_name = path.basename(items[0])
        self.folders_tab.addTab(
            self.list_widget, trim_text(folder_name, 15) if folder_name else items[0])
        self.folders_tab.adjustSize()

    def close(self, layout):
        """
            delete widgets recursively
        """

        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                widget = child.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.close(child.layout())

    def create_banner(self, msg: str):
        """
            create a banner to communicate to the user
        """

        self.close(self.main_layout)
        self.msg_label = QLabel(parent=self.disk_management_win)
        # self.close_msg_button.clicked.connect(self.create_disk_win)
        self.msg_label.setText(msg)
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.msg_label)
        self.disk_management_win.setLayout(self.main_layout)


def trim_text(txt: str, length: int) -> str:
    """
        reduce the length of a string to the specified len
    """
    if len(txt) > length:
        return f"{txt[:length]}..."
    else:
        return txt


# ------------------------------------- MAIN WINDOW -----------------------------------------
class MainWindow(QWidget):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("asfa")
        self.setMinimumSize(QSize(1200, 600))
        self.setWindowIcon(QIcon("data\\asfa.png"))
        # window icons
        self.download_icon = QIcon("data\\download.png")
        self.upload_icon = QIcon("data\\upload.png")
        self.done_icon = QIcon("data\\done.png")
        self.login_icon = QIcon("data\\login.png")
        self.cancel_icon = QIcon("data\\cancel.png")
        self.logout_icon = QIcon("data\\logout.png")

        self.vlayout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        # set the main window layout
        self.setLayout(self.vlayout)
        # add widgets to the layout
        self.main_tab = QTabWidget()
        self.main_tab.setDocumentMode(1)
        # set qss style
        # self.main_tab.setStyleSheet("font: 16pts")
        # modify the font
        font = self.main_tab.font()
        font.setPointSize(16)
        self.main_tab.setFont(font)
        # ; border-radius: 15px; border: 2px solid black
        # create the window to hold widgets that will go in the first tab
        self.disk_man = DiskMan()
        # self.disk_man.create_banner("Insert Drive")
        self.main_tab.insertTab(
            0, self.disk_man.disk_management_win, "External Storage")
        # for the second tab
        self.create_share_win()
        # create downloads tab
        self.create_downloads_win()
        # create the status bars
        self.left_statusbar = QLabel("left: 123 MB")
        self.center_statusbar = QLabel("center: 790 MB")
        self.right_statusbar = QLabel("right: 56 / 83 MB")
        # add to horizontal layout
        self.hlayout.addWidget(self.left_statusbar)
        self.hlayout.addWidget(self.center_statusbar)
        self.hlayout.addWidget(self.right_statusbar)
        self.hlayout.setSpacing(2)
        # add the tab widget to the layout
        self.vlayout.addWidget(self.main_tab)
        # nest the status bar layout in the vertical main layout
        self.vlayout.addLayout(self.hlayout)

    def create_share_win(self):
        """
            create the window to hold widgets
            that will go in the file sharing tab
        """

        self.file_share_win = QWidget()
        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        # use v layout for this widget
        self.file_share_win.setLayout(vlayout)
        # create the control buttons
        self.upload_button = QPushButton("Upload")
        self.upload_button.setIcon(self.upload_icon)
        self.download_button = QPushButton("Download")
        self.download_button.setIcon(self.download_icon)
        self.login_button = QPushButton("Login")
        self.login_button.setIcon(self.login_icon)
        self.logout_button = QPushButton("Logout")
        self.logout_button.setIcon(self.logout_icon)
        # add to the top in a horizontal manner
        hlayout.addWidget(self.upload_button)
        hlayout.addWidget(self.download_button)
        hlayout.addStretch()
        hlayout.addWidget(self.login_button)
        hlayout.addWidget(self.logout_button)
        # nest an inner layout
        vlayout.addLayout(hlayout)
        # create area for files display
        # use Grid layout
        self.files_area = QWidget()
        self.files_area.setStyleSheet("background: white")
        # scroll = QScrollArea()
        # scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # scroll.setWidgetResizable(1)
        # scroll.setWidget(self.files_area)
        inner_vlayout = QVBoxLayout()
        # inner_vlayout.addWidget(scroll)
        inner_vlayout.addWidget(MessageBox(msg="Hello, people!"))
        inner_vlayout.addWidget(MessageBox(reply="Hey there..."))
        inner_vlayout.addWidget(MessageBox())
        inner_vlayout.addWidget(MessageBox())
        inner_vlayout.addWidget(MessageBox(msg="Hello, people!"))
        inner_vlayout.addStretch()
        self.files_area.setLayout(inner_vlayout)
        # TODO: update files here
        # add this tab to the vertical layout
        vlayout.addWidget(self.files_area)
        # add this window to the tab
        self.main_tab.addTab(self.file_share_win, "Share Files")

    def create_downloads_win(self):
        """
            create the window to hold widgets
            that will go in the downloads tab
        """

        # create area for displaying downloaded files
        self.downloads_area = QWidget()
        vlayout = QVBoxLayout()
        vlayout.setSpacing(3)
        # TODO: update files here
        items = (["34.2/56.1MB | Filename.mp3", False],
                 ["Downloaded filename.mp4", True], ["S2E4.mkv", True])
        for item, downloaded in items:
            if downloaded:
                row = DownloadDialog(item, "Open")
                row.button.setIcon(self.disk_man.open_icon)
            else:
                row = DownloadDialog(item, "Cancel")
                row.button.setIcon(self.cancel_icon)
            vlayout.addWidget(row)
        # stretch only the empty space below the widgets
        vlayout.addStretch()
        self.downloads_area.setLayout(vlayout)
        # add this window to the tab
        self.main_tab.addTab(self.downloads_area, "Downloads")
        # self.main_tab.setTabIcon()

    def banner(self, msg):
        """
            Inform the user of the msg
        """
        self.disk_man.create_banner(msg)

    def ask(self, qtn):
        """
            ask confirm questions
        """

        return QMessageBox.question(self, "asfa - Confirmation", qtn, defaultButton=QMessageBox.Yes)
# -------------------------------------- END OF MAIN WINDOW ----------------------------------------


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    file = "C:\\Users\\code\\Pictures\\add_121935.png"
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    w = MainWindow()

    # w.resize(640, 480)
    w.show()

    sys.exit(app.exec_())
