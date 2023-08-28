__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"

from typing import List
import os
from qss import QSS
import usb
import asfaUtils
import psutil
from asfaModel import SortFilterModel, TableModel
from PyQt5.QtCore import Qt, QSize, QRect, QPoint, QThreadPool, QModelIndex
from PyQt5.QtGui import (
    QIcon,
    QStandardItemModel,
    QStandardItem,
    QKeySequence)
from PyQt5.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QWidgetAction,
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QPushButton,
    QWidget,
    QShortcut,
    QStyle, QMenu,
    QTabBar,
    QStylePainter,
    QStyleOptionTab,
    QTabWidget,
    QFrame, QAction,
    QVBoxLayout, QHBoxLayout,
    QLineEdit,
    QTableView,
    QScrollArea,
    QCheckBox,
    QMessageBox,
    QRadioButton)


class TrayMenu(QMenu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # declare icons
        self.video_icon = QIcon("data\\videos.png")
        self.doc_icon = QIcon("data\\doc.png")
        self.audio_icon = QIcon("data\\audio.png")
        self.image_icon = QIcon("data\\images.png")

        # header row
        self.tray_header = QLabel(self)
        self.tray_header.setText("Insert Disk")
        self.tray_header.setAlignment(Qt.AlignCenter)
        self.tray_header.setStyleSheet("color: white; background: #008fcc; font: 17px")
        header_row = QWidgetAction(self)
        header_row.setDefaultWidget(self.tray_header)
        self.addAction(header_row)
        # rbuttons row
        rbuttons_holder = QWidget(self)
        hlayout = QHBoxLayout(self)
        # hlayout.setContentsMargins(0, 0, 0, 0)
        self.copy_rbutton = QRadioButton("Copy")
        self.copy_rbutton.clicked.connect(self.copy_selected)
        self.copy_rbutton.click()
        self.cut_rbutton = QRadioButton("Cut")
        self.cut_rbutton.clicked.connect(self.cut_selected)
        hlayout.addWidget(self.copy_rbutton, alignment=Qt.AlignRight)
        hlayout.addWidget(self.cut_rbutton, alignment=Qt.AlignRight)
        rbuttons_holder.setLayout(hlayout)
        rbuttons_row = QWidgetAction(self)
        rbuttons_row.setDefaultWidget(rbuttons_holder)
        self.addAction(rbuttons_row)

        self.videos_action = QAction(self.video_icon, f"{self.selected} all Videos")
        self.doc_action = QAction(self.doc_icon, f"{self.selected} all Documents")
        self.audio_action = QAction(self.audio_icon, f"{self.selected} all Audio")
        self.images_action = QAction(self.image_icon, f"{self.selected} all Images")
        self.create_buttons()

    def create_videos_action(self):
        # videos present
        # self.videos_action.triggered.connect
        self.insertAction(self.last_action, self.videos_action)

    def create_documents_action(self):
        # documents present
        self.insertAction(self.last_action, self.doc_action)

    def create_audio_action(self):
        # audio present
        self.insertAction(self.last_action, self.audio_action)

    def create_images_action(self):
        # images present
        self.insertAction(self.last_action, self.images_action)

    def create_buttons(self):
        # quit and more buttons
        self.addSeparator()
        self.abuttons_holder = QWidget(self)
        hlayout = QHBoxLayout(self)
        self.quit = QPushButton("Quit")
        self.more = QPushButton("More")
        hlayout.addWidget(self.quit)
        hlayout.addWidget(self.more)
        self.abuttons_holder.setLayout(hlayout)
        self.last_action = QWidgetAction(self)
        self.last_action.setDefaultWidget(self.abuttons_holder)
        self.addAction(self.last_action)

    def create_all(self):
        self.create_videos_action()
        self.create_documents_action()
        self.create_audio_action()
        self.create_images_action()

    def copy_selected(self):
        self.selected = "Copy"
        self.update_text()

    def cut_selected(self):
        self.selected = "Cut"
        self.update_text()

    def update_text(self):
        try:
            self.videos_action.setText(f"{self.selected} all Videos")
            self.doc_action.setText(f"{self.selected} all Documents")
            self.audio_action.setText(f"{self.selected} all Audio")
            self.images_action.setText(f"{self.selected} all Images")
        except AttributeError:
            pass


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
        self.disk_management_win = QWidget()
        self.main_layout = QVBoxLayout()
        self.search_icon = QIcon("data\\search.png")
        self.available_file_types = set()
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
        self.disk_stats_label = QLabel()
        # create search area
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files in all folders")
        input_layout = QHBoxLayout(self.search_input)
        input_layout.setContentsMargins(0, 0, 0, 0)
        self.search_button = QPushButton(self.search_input)
        self.search_button.setIcon(self.search_icon)
        self.search_button.setCursor(Qt.ArrowCursor)
        input_layout.addWidget(self.search_button, alignment=Qt.AlignVCenter | Qt.AlignRight)
        hlayout.addWidget(self.disk_stats_label)
        hlayout.addStretch()
        hlayout.addWidget(self.search_input)
        # nest an inner layout
        self.main_layout.addLayout(hlayout)
        # create the inner vertical tab widget
        self.drives_tab = TabWidget()
        self.drives_tab.setMovable(1)
        self.drives_tab.setDocumentMode(1)
        self.main_layout.addWidget(self.drives_tab)

    def create_files_list(self, generators: list, tab_name):
        """
            create a table to show files in different folders
        """

        model = TableModel(generators, ("Name", "File Path", "Type", "Size"))

        # print(model.rowCount())
        filter_proxy_model = SortFilterModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(-1)

        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(0)
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setModel(filter_proxy_model)
        self.table.setSortingEnabled(1)
        self.table.setShowGrid(0)
        self.table.setAlternatingRowColors(1)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.drives_tab.addTab(self.table, tab_name[:2])
        self.drives_tab.adjustSize()

    def close_files_list(self, index: int):
        """
            remove the specified tab index
        """

        self.table.deleteLater()
        self.drives_tab.removeTab(index)

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


# ------------------------------------- MAIN WINDOW -----------------------------------------
class MainWindow(QWidget):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("asfa")
        self.setMinimumSize(QSize(1200, 600))
        self.app_icon = QIcon("data\\asfa.png")
        self.setWindowIcon(self.app_icon)
        # window icons
        self.download_icon = QIcon("data\\download.png")
        self.upload_icon = QIcon("data\\upload.png")
        self.done_icon = QIcon("data\\done.png")
        self.login_icon = QIcon("data\\login.png")
        self.cancel_icon = QIcon("data\\cancel.png")
        self.logout_icon = QIcon("data\\logout.png")
        self.copy_icon = QIcon("data\\copy.png")
        self.cut_icon = QIcon("data\\cut.png")
        self.delete_icon = QIcon("data\\delete.png")
        self.open_icon = QIcon("data\\open.png")
        self.select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        self.on_search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)

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
        font.setPointSize(14)
        self.main_tab.setFont(font)
        # ; border-radius: 15px; border: 2px solid black
        # create the window to hold widgets that will go in the first tab
        self.disk_man = DiskMan()
        # self.disk_man.create_banner("Insert Disk")
        self.main_tab.insertTab(0, self.disk_man.disk_management_win, "External Storage")
        # create the first tab
        self.disk_man.create_disk_win()
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
                row.button.setIcon(self.open_icon)
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

    def ask(self, qtn):
        """
            ask confirm questions
        """

        return QMessageBox.question(self, "asfa - Confirmation", qtn, defaultButton=QMessageBox.Yes)
# -------------------------------------- END OF MAIN WINDOW ----------------------------------------


class Controller(MainWindow):
    """
        the brain for controlling asfa GUI and its data
        TODO: handle 200k files for slow computers - scalability
    """

    def __init__(self):
        super().__init__()
        # self.folders = []
        self.available_disks = set()
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.app_icon)
        self.tray.setToolTip("asfa")
        self.tray_menu = TrayMenu(self)
        self.tray_menu.create_all()
        self.tray_menu.more.clicked.connect(self.show_main_window)
        self.tray.setContextMenu(self.tray_menu)
        # create disk window/tab
        self.disk_man.create_disk_win()
        # call tab_changed whenever current tab changes
        self.disk_man.drives_tab.currentChanged.connect(self.tab_changed)

        self.set_path(os.path.expanduser("~\\Downloads"))
        # set shortcuts
        self.on_search_shortcut.activated.connect(self.disk_man.search_input.setFocus)
        # start the usb listener
        self.threadpool = QThreadPool()
        self.usb_thread = usb.DeviceListener()
        self.on_startup(self.usb_thread.disks)
        self.usb_thread.signals.on_change.connect(self.on_disk_changes)
        self.usb_thread.signals.error.connect(self.disk_man.create_banner)
        self.threadpool.start(self.usb_thread)
        # set event callbacks
        self.disk_man.search_input.textChanged.connect(self.search)
        self.show()
        # self.tray.show()
        # self.tray.showMessage("asfa is running here", "Right-click the icon for more options", self.app_icon)
        self.routes = {Qt.Key_Enter: self.open_file, Qt.Key_Return: self.open_file, Qt.Key_Delete: self.delete_files}
        # simulate a tab changed on startup
        self.tab_changed()

    def tab_changed(self):
        """
            on drive tab change event
            get the current table, model and update the slots
        """

        self.table_view = self.disk_man.drives_tab.currentWidget()
        self.current_disk_index = self.disk_man.drives_tab.currentIndex()
        self.current_disk_name = self.disk_man.drives_tab.tabText(self.current_disk_index)
        self.table_view.doubleClicked.connect(self.on_double_click)
        # select all Ctrl+A shortcut
        self.select_all_shortcut.activated.connect(self.table_view.selectAll)
        # set focus on table
        self.table_view.setFocus()
        self.model = self.table_view.model()
        self.selection_model = self.table_view.selectionModel()
        self.close_search()
        # show stats per disk
        self.update_stats()

    @property
    def selected_rows(self) -> List[QModelIndex]:
        """
            get the currently selected rows
        """

        return self.selection_model.selectedRows()

    @property
    def total_files(self) -> int:
        """
            get all files
        """

        return self.model.rowCount()

    @property
    def isTableFocused(self) -> bool:
        """
            check if table view is under mouse and focused
        """

        return (self.table_view.underMouse() and self.table_view.hasFocus())

    def update_stats(self):
        """
            update info about files on main window and on tray
        """

        self.disk_man.disk_stats_label.setText(f"Disk: {self.current_disk_name}, Files: {self.total_files}")
        self.tray_menu.tray_header.setText(f"Disk: {self.current_disk_name}, Files: {self.total_files}")

    def closeEvent(self, e):
        """
            minimize on close and notify user
        """

        self.tray.show()
        # self.tray.showMessage("asfa is minimized here", "Right-click for Quit option", self.app_icon)
        self.hide()
        e.ignore()

    def show_main_window(self):
        """
            slot for 'more' button in tray
        """

        self.tray.hide()
        # show window normally
        self.showNormal()

    def contextMenuEvent(self, e):
        if self.isTableFocused:

            self.context = QMenu(self)
            # addAction(self, QIcon, str, PYQT_SLOT, shortcut: Union[QKeySequence, QKeySequence.StandardKey, str, int] = 0)
            self.context.addAction(self.open_icon, "Open", self.open_file)
            self.context.addSeparator()
            self.context.addAction(self.copy_icon, "Copy", self.copy, "Ctrl+C")
            self.context.addAction(self.cut_icon, "Cut", self.cut, "Ctrl+X")
            self.context.addSeparator()
            self.context.addAction(self.delete_icon, "Delete", self.delete_files)
            self.context.exec_(e.globalPos())

    def keyPressEvent(self, e):
        """
            route key presses to their respective slots
        """

        if self.isTableFocused:
            func = self.routes.get(e.key())
            if func:
                func()

    def on_startup(self, listdrives):
        """
            get disks and setup on startup
        """

        if listdrives:
            self.available_disks = {d.letter for d in listdrives}
            self.set_path(list(self.available_disks)[0])
        else:
            self.disk_man.create_banner("Insert Disk")

    def set_path(self, path: str):
        """
            update current folders and setup model/view
        """

        folders = asfaUtils.get_folders(path)
        file_generators = [asfaUtils.get_files(folder) for folder in folders]
        self.disk_man.create_files_list(file_generators, path)

    def on_disk_changes(self, listdrives):
        """
            respond to disk insert/eject
        """

        if listdrives:
            disks = {d.letter for d in listdrives}
            ejected = self.available_disks.difference(disks)
            inserted = disks.difference(self.available_disks)
            self.available_disks = disks
            if inserted:
                disk = inserted.pop()
                self.set_path(disk)
                self.tray.showMessage(f"asfa has detected Disk {disk}", "Transfer files here", self.app_icon)
            elif ejected:
                index = self.index_from_tabText(ejected.pop())
                self.disk_man.close_files_list(index)
        else:
            self.available_disks = set()
            self.disk_man.create_banner("Insert Disk")

    def on_search(self):
        """
            slot for search button
        """

        string = self.disk_man.search_input.text()
        self.search(string)

    def search(self, search_txt):
        """
            change the search button icon and set the filter txt
            callback for QLineEdit textChanged event
        """

        if search_txt:
            self.model.setFilterRegExp(search_txt)
            self.disk_man.search_button.setIcon(self.cancel_icon)
            self.disk_man.search_button.clicked.connect(self.close_search)
        else:
            self.close_search()

    def close_search(self):
        """
            close a search and update the search button icon
        """

        self.disk_man.search_button.setIcon(self.disk_man.search_icon)
        self.disk_man.search_button.clicked.connect(self.on_search)
        self.disk_man.search_input.clear()
        self.model.setFilterRegExp("")

    def on_double_click(self, s: QModelIndex):
        """
            open a file on double-click
        """

        path = self.path_from_row(s)
        print(path)
        asfaUtils.start_file(path)

    def path_from_row(self, row: QModelIndex):
        """
            get data from the first and the second column of row
            join them and return full file path
        """

        row = row.row()
        dirname = self.model.data(self.model.index(row, 1))
        file = self.model.data(self.model.index(row, 0))
        return os.path.join(dirname, file)

    def index_from_tabText(self, txt) -> int:
        """
            return the index of the tab with txt; suppose no duplicated tab name
        """

        for i in range(self.disk_man.drives_tab.count()):
            if txt == self.disk_man.drives_tab.tabText(i):
                return i

    def delete_files(self):
        """
            remove selected rows and delete assc'd files
        """

        confirmation = self.ask(f"Delete {len(self.selected_rows)} selected file(s) permanently?")
        # if confirmation is YES
        if confirmation == 16384:
            for index in self.selected_rows[::-1]:
                path = self.path_from_row(index)
                asfaUtils.delete_file(path)
                self.model.removeRow(index.row())
            self.update_stats()

    def open_file(self):
        """
            open last-selected file
        """

        path = self.path_from_row(self.selected_rows[-1])
        asfaUtils.start_file(path)

    def copy(self):
        """
            copy files
        """

        pass

    def cut(self):
        """
            cut files
        """

        pass


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    # app.setStyleSheet(QSS)

    def close_win():

        # c.tray.hide()
        c.usb_thread.close()
        app.quit()
        sys.exit(0)
        


    c = Controller()
    c.tray_menu.quit.clicked.connect(close_win)

    # memory usage in MBs
    memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1048576
    print(f"[MEMORY USED] : {memory_usage} MB")

    sys.exit(app.exec_())
