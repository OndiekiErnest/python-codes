__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


from typing import List, Iterable, Generator
from network import server, browser
import common
import os
from qss import QSS
import asfaUtils
import asfaDownloads
import psutil
from asfaModel import SortFilterModel, ShareFilesModel
from PyQt5.QtCore import Qt, QSize, QRect, QPoint, QThreadPool, QModelIndex, QTimer
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
    QLabel, QFileDialog,
    QPushButton,
    QWidget, QSlider,
    QShortcut, QListWidget,
    QStyle, QMenu,
    QTabBar, QComboBox,
    QStylePainter,
    QStyleOptionTab,
    QTabWidget,
    QFrame, QAction,
    QVBoxLayout, QHBoxLayout,
    QLineEdit, QFormLayout,
    QTableView,
    QCheckBox, QProgressBar,
    QMessageBox)


class TrayMenu(QMenu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # header row
        self.to_transfer_win = QPushButton("Transfer files", self)
        header_row = QWidgetAction(self)
        header_row.setDefaultWidget(self.to_transfer_win)
        self.addAction(header_row)

        self.create_buttons()

    def create_buttons(self):
        # quit and more buttons
        self.addSeparator()
        self.abuttons_holder = QWidget(self)
        hlayout = QHBoxLayout(self)
        self.quit = QPushButton("Quit")
        self.more = QPushButton("More")
        hlayout.addWidget(self.more)
        hlayout.addWidget(self.quit)
        self.abuttons_holder.setLayout(hlayout)
        self.last_action = QWidgetAction(self)
        self.last_action.setDefaultWidget(self.abuttons_holder)
        self.addAction(self.last_action)

    def update_disk_folders(self, disk_path: str):
        self.from_folder.clear()
        if disk_path:
            self.from_folder.addItems(asfaUtils.get_folders(disk_path))


class DuplicatesWindow(QWidget):

    def __init__(self, files: Iterable[str], *args):
        """
        window for displaying duplicate files
        inherits:
            QWidget
        """
        super().__init__(*args)
        self.setWindowTitle("Feedback - asfa")
        self.setFixedSize(450, 200)

        btns_layout = QHBoxLayout()
        vlayout = QVBoxLayout()

        details_label = QLabel("These files already exist:", self)
        list_widget = QListWidget(self)
        list_widget.addItems(files)
        ok_btn = QPushButton("OK", self)
        ok_btn.clicked.connect(self.deleteLater)
        btns_layout.addWidget(ok_btn, alignment=Qt.AlignRight)

        vlayout.addWidget(details_label)
        vlayout.addWidget(list_widget)
        vlayout.addLayout(btns_layout)
        self.setLayout(vlayout)


class TransferWindow(QWidget):

    def __init__(self, *args):
        """
        window for displaying transfer progress
        inherits:
            QWidget
        """
        super().__init__(*args)
        self.setWindowTitle("Transfering - asfa")
        self.setFixedSize(400, 150)

        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        self.cancel_transfer = QPushButton("Cancel", self)
        btn_layout.addWidget(self.cancel_transfer, alignment=Qt.AlignRight)
        self.transfer_to = QLabel("Transfering to:", self)
        self.percentage_progress = QLabel("0%", self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(0)
        self.remaining_files = QLabel("0 Files Remaining", self)
        main_layout.addWidget(self.transfer_to)
        main_layout.addWidget(self.percentage_progress)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.remaining_files)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)


class WorkerManager(TransferWindow):
    """
    Manager to handle our worker queues and state
    inherits:
        TransferWindow: transfer GUI
    assumes:
        all workers/runnables are the same
    """

    _workers_progress = {}
    _active_workers = {}
    _transferred = {}

    def __init__(self):
        super().__init__()
        # Create a threadpool for workers
        self.files_threadpool = QThreadPool()
        self.files_threadpool.setMaxThreadCount(2)
        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.refresh_progress)
        self.timer.start()
        self.total_workers = 0
        self.total_size = 0
        self.duplicates = []
        self.max_threads = self.files_threadpool.maxThreadCount()
        print("Can transfer  %d files at a time" % self.max_threads)
        self.cancel_transfer.clicked.connect(self.cancel)

    def enqueue(self, worker: asfaUtils.Transfer):
        """ Enqueue a worker to run (at some point) by passing it to the QThreadPool """

        worker.signals.progress.connect(self.receive_progress)
        worker.signals.finished.connect(self.done)
        worker.signals.transferred.connect(self.receive_transferred)
        self.files_threadpool.start(worker)
        self._active_workers[worker.job_id] = worker
        self.total_workers += 1
        self.total_size += worker.size
        self.show()

    def receive_progress(self, job_id, progress):
        self._workers_progress[job_id] = progress

    def receive_transferred(self, job_id, size):
        self._transferred[job_id] = size

    def calculate_progress(self):
        """ Calculate total progress """
        if not self._workers_progress:
            return 0
        return sum(v for v in self._workers_progress.values()) / self.total_workers

    def calculate_transferred(self):
        if not self._transferred:
            return 0
        return sum(v for v in self._transferred.values())

    def refresh_progress(self):
        """ get and update progress """
        progress = int(self.calculate_progress())
        transferred = self.calculate_transferred()
        rem_size = common.convert_bytes(self.total_size - transferred)
        rem_files = max(1, len(self._active_workers))

        self.progress_bar.setValue(progress)
        self.percentage_progress.setText(f"{progress}%")
        self.remaining_files.setText(f"{rem_files} remaining ({rem_size})")

    def done(self, job_id):
        """ Remove workers when all jobs are done 100% """
        # avoid KeyError
        if self._active_workers:
            del self._active_workers[job_id]
        if all(v == 100 for v in self._workers_progress.values()) and not (self._active_workers):
            self._workers_progress.clear()
            self._transferred.clear()
            self.total_workers = 0
            self.total_size = 0
            self.handle_dups()
            self.hide()

    def cancel(self):
        """ cancel transfer """
        self.files_threadpool.clear()
        for w in self._active_workers.values():
            w.running = 0
        self._active_workers.clear()
        self.hide()

    def handle_dups(self):
        if self.duplicates:
            self.w = DuplicatesWindow(self.duplicates)
            self.w.setWindowIcon(self.windowIcon())
            self.duplicates.clear()
            self.w.show()


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

    def update_w(self, labeltxt, buttontxt):
        self.label.setText(labeltxt)
        self.button.setText(buttontxt)
        if buttontxt == "Open":
            # link button to open_files function
            pass
        else:
            self.button.clicked.connect(lambda: asfaUtils.close_window(self.layout))


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


class DiskManager(QWidget):
    """
        disk window widget
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # window icons
        self.main_layout = QVBoxLayout()
        self.search_icon = QIcon("data\\search.png")
        self.on_banner = 0
        # self.main_layout = None
        self.on_search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.cut_shortcut = QShortcut(QKeySequence("Ctrl+X"), self)

    def create_disk_win(self):
        """
            create the window to hold widgets
            that will go in the disk management tab
        """

        asfaUtils.close_window(self.main_layout)
        hlayout = QHBoxLayout()
        # use v layout for this widget
        self.setLayout(self.main_layout)
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
        self.on_banner = 0

    def create_files_list(self, generators: Iterable[Generator], tab_name):
        """
            create a table to show files in different folders
        """

        # create folder watcher using tab_name
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Name", "File Path", "Type", "Size"])

        for generator in generators:
            for row in generator:
                name = QStandardItem(row[0])
                name.setToolTip(row[0])
                file_path = QStandardItem(row[1])
                file_path.setToolTip(row[1])
                file_path.setTextAlignment(Qt.AlignCenter)
                type_column = QStandardItem(row[2])
                type_column.setTextAlignment(Qt.AlignCenter)
                size_column = QStandardItem(row[3])
                size_column.setTextAlignment(Qt.AlignCenter)

                model.appendRow((name, file_path, type_column, size_column))

        filter_proxy_model = SortFilterModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(-1)

        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(0)
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

        self.drives_tab.removeTab(index)

    def add_file(self, file):
        # format the file str first
        name, folder, ext, size = asfaUtils.get_file_details(file)
        name_column = QStandardItem(name)
        name_column.setToolTip(name)
        path_column = QStandardItem(folder)
        path_column.setToolTip(folder)
        path_column.setTextAlignment(Qt.AlignCenter)
        type_column = QStandardItem(ext)
        type_column.setTextAlignment(Qt.AlignCenter)
        size_column = QStandardItem(size)
        size_column.setTextAlignment(Qt.AlignCenter)
        model = self.table.model()
        model.insertRow(0, (name_column, path_column, type_column, size_column))

    def create_banner(self, msg: str):
        """
            create a banner to communicate to the user
        """

        asfaUtils.close_window(self.main_layout)
        self.msg_label = QLabel(parent=self)
        self.msg_label.setText(msg)
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.msg_label)
        self.setLayout(self.main_layout)
        # banner flag
        self.on_banner = 1


class ShareManager(QWidget):
    """
        share window manager
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tick_icon = QIcon("data\\tick.png")
        arrow_icon = QIcon("data\\arrow.png")
        loading_icon = QIcon("data\\load.png")
        back_icon = QIcon("data\\back.png")
        refresh_icon = QIcon("data\\refresh.png")
        self.icons = {0: arrow_icon, 1: tick_icon, 2: loading_icon}
        self.main_layout = QVBoxLayout()
        # use v layout for this widget
        self.setLayout(self.main_layout)
        self.files_chooser_btn = QPushButton("Upload")
        self.files_chooser_btn.clicked.connect(self.files_chooser)
        self.download_btn = QPushButton("Download")
        self.back_folder = QPushButton()
        self.back_folder.setIcon(back_icon)
        self.show_current_folder = QLineEdit("Home:\\")
        self.show_current_folder.setReadOnly(1)
        self.refresh_shared_files = QPushButton()
        self.refresh_shared_files.setIcon(refresh_icon)
        self.online_status_label = QLabel("Online:")
        self.online_users_dropdown = QComboBox()
        self.on_banner = 0

    def create_share_win(self):
        """
            create the window for share files tab
        """

        asfaUtils.close_window(self.main_layout)
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.files_chooser_btn)
        hlayout.addWidget(self.download_btn)
        hlayout.addWidget(self.back_folder)
        hlayout.addWidget(self.show_current_folder)
        hlayout.addWidget(self.refresh_shared_files)
        # hlayout.addStretch()
        hlayout.addWidget(self.online_status_label)
        hlayout.addWidget(self.online_users_dropdown)
        # nest the inner hlayout
        self.main_layout.addLayout(hlayout)
        # create table for files display

        self.share_table = QTableView()
        self.share_table.clicked.connect(self.on_click)
        self.main_layout.addWidget(self.share_table)
        self.on_banner = 0

    def files_chooser(self):
        upload_files = QFileDialog.getOpenFileNames(self, "asfa - Choose folder")[0]
        if upload_files:
            print(upload_files)

    def on_click(self, index):
        # print(index.row(), index.data())
        pass

    def add_files(self, generator: Generator):
        """
            create a table to show shared generator
        """

        self.share_model = ShareFilesModel(generator, ("Name", "Status", "Type", "Size"), self.icons)

        self.share_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.share_table.verticalHeader().setVisible(0)
        self.share_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.share_table.setModel(self.share_model)
        self.share_table.setSortingEnabled(1)
        self.share_table.setShowGrid(0)
        # self.share_table.setAlternatingRowColors(1)
        self.share_table.setEditTriggers(self.share_table.NoEditTriggers)

    def create_banner(self, msg: str):
        """
            create a banner to communicate to the user
        """

        asfaUtils.close_window(self.main_layout)
        self.msg_label = QLabel(parent=self)
        # self.close_msg_button.clicked.connect(self.create_disk_win)
        self.msg_label.setText(msg)
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.msg_label)
        self.setLayout(self.main_layout)
        # banner flag
        self.on_banner = 1


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

        self.vlayout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        # set the main window layout
        self.setLayout(self.vlayout)
        # add widgets to the layout
        self.main_tab = QTabWidget()
        self.main_tab.setDocumentMode(1)
        # modify the font
        font = self.main_tab.font()
        font.setPointSize(14)
        self.main_tab.setFont(font)
        # create the window to hold widgets that will go in the first tab
        self.disk_man = DiskManager(self)
        # self.disk_man.create_banner("Insert Disk")
        self.main_tab.insertTab(0, self.disk_man, "External Storage")
        # create the first tab
        self.disk_man.create_disk_win()
        # for the second tab
        self.share_man = ShareManager(self)
        self.share_man.create_share_win()
        self.main_tab.addTab(self.share_man, "Share Files")

        # prepare downloads window
        self.downloads_win = asfaDownloads.DownloadsWindow()

        # create settings tab
        self.create_settings_win()
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

    def create_settings_win(self):
        """
            create the window to hold widgets
            that will go in the downloads tab
        """

        # create area for displaying downloaded files
        self.downloads_area = QWidget()
        speed_layout = QHBoxLayout()
        form_layout = QFormLayout()
        # create settings fields
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.shared_folder = QLineEdit()
        self.shared_folder.setPlaceholderText("Select a shared folder")

        self.speed_limiter = QSlider()
        self.speed_limiter.setOrientation(Qt.Horizontal)
        self.speed_limiter.setTickPosition(self.speed_limiter.TicksBelow)
        self.speed_limiter.setTickInterval(1)
        self.speed_limiter.setRange(2, 10)
        speed_label = QLabel("2")
        self.speed_limiter.valueChanged.connect(lambda s: speed_label.setText(str(s)))
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_limiter)
        self.download_location = QLineEdit()
        self.download_location.setPlaceholderText("Select downloads folder")

        form_layout.addRow("Username", self.username_input)
        form_layout.addRow(QPushButton("Shared folder"), self.shared_folder)
        form_layout.addRow("Speed limit", speed_layout)
        form_layout.addRow(QPushButton("Download location"), self.download_location)
        self.downloads_area.setLayout(form_layout)
        # add this window to the tab
        self.main_tab.addTab(self.downloads_area, "Settings")

    def ask(self, qtn):
        """
            ask confirm questions
        """

        return QMessageBox.question(self, "Confirmation - asfa", qtn, defaultButton=QMessageBox.Yes)

    def inform(self, info):
        """ send information to the user """
        return QMessageBox.information(self, "Information - asfa", info)
# -------------------------------------- END OF MAIN WINDOW ----------------------------------------


class Controller(MainWindow):
    """
    the brain for controlling asfa GUI and its data models
    TODO: handle 200k files with ease - scalability
    """

    def __init__(self):
        super().__init__()

        self.show()
        self.main_tab.currentChanged.connect(self.main_tab_changed)
        self.available_disks = set()
        self.those_online = set()

        # system tray icon
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.app_icon)
        self.tray.setToolTip("asfa")
        self.tray_menu = TrayMenu(self)
        self.tray_menu.more.clicked.connect(self.show_main_window)
        self.tray.setContextMenu(self.tray_menu)

        # share window
        # self.broadcaster = asfaUtils.BroadcastUser()
        # self.broadcaster.start()
        # self.receive_users = asfaUtils.ReceiveUser()
        # self.receive_users.new_user.connect(self.update_new_user)
        # self.receive_users.start()
        # server uses local machine's IP
        self.server = server.Server()
        self.server.setSharedDirectory(os.path.expanduser("~\\Downloads"))
        self.server.start()
        self.server_browser = browser.ServerBrowser()
        # the IP address for the remote machine
        self.server_browser.updateHost(("192.168.43.211", 2121))
        self.update_shared_files()

        # set KeyBoard shortcuts
        self.disk_man.copy_shortcut.activated.connect(self.copy)
        self.disk_man.cut_shortcut.activated.connect(self.cut)
        self.disk_man.select_all_shortcut.activated.connect(self.select_all)
        # set focus shortcut
        self.disk_man.on_search_shortcut.activated.connect(self.focus_search_input)

        # downloads
        self.share_man.download_btn.clicked.connect(self.download_clicked)
        self.share_man.back_folder.clicked.connect(self.back_to_folder)
        self.share_man.share_table.doubleClicked.connect(self.share_double_click)
        self.share_man.share_table.selectionModel().selectionChanged.connect(self.get_properties)
        self.share_man.refresh_shared_files.clicked.connect(self.update_shared_files)

        # self.set_path(os.path.expanduser("~\\Downloads"))
        self.worker_manager = WorkerManager()
        self.worker_manager.setWindowIcon(self.app_icon)

        # start the usb listener thread
        self.usb_thread = asfaUtils.DeviceListener()
        self.on_startup(self.usb_thread.disks)
        self.usb_thread.signals.on_change.connect(self.on_disk_changes)
        self.usb_thread.signals.error.connect(self.disk_man.create_banner)
        self.usb_thread.start()
        # self.tray.show()
        # self.tray.showMessage("asfa is running here", "Right-click the icon for more options", self.app_icon)
        self.key_routes = {Qt.Key_Enter: self.open_file, Qt.Key_Return: self.open_file, Qt.Key_Delete: self.delete_files}
        self.sharefiles_routes = {Qt.Key_Enter: self.share_open_file, Qt.Key_Return: self.share_open_file}

    def main_tab_changed(self):
        """ called when main tabs are switched """
        self.get_properties()

    def tab_changed(self):
        """
        on drive tab change event
        get the current table, model and update the slots
        """

        try:
            self.close_search()
        except AttributeError:
            pass
        self.table_view = self.disk_man.drives_tab.currentWidget()
        current_disk_index = self.disk_man.drives_tab.currentIndex()
        self.current_disk_name = self.disk_man.drives_tab.tabText(current_disk_index)
        # set focus on table
        self.table_view.setFocus()
        self.files_model = self.table_view.model()
        self.selection_model = self.table_view.selectionModel()
        self.selection_model.selectionChanged.connect(self.get_properties)
        # show stats per disk
        self.update_stats()
        self.get_properties()

    @property
    def selected_rows(self) -> List[QModelIndex]:
        """
        get the currently selected rows
        """
        try:
            return tuple(self.selection_model.selectedRows())
        except Exception:
            return ()

    @property
    def total_files(self) -> int:
        """
        get all files
        """

        return self.files_model.rowCount()

    @property
    def isDiskTableFocused(self) -> bool:
        """
        check if table view is under mouse and focused
        """
        try:
            return (self.table_view.underMouse() and self.table_view.hasFocus())
        except Exception:
            return 0

    @property
    def isShareTableFocused(self) -> bool:
        try:
            table = self.share_man.share_table
            return (table.underMouse() and table.hasFocus())
        except Exception:
            return 0

    def get_properties(self, selected=None, deselected=None):
        """
        get the total size of all the selected files
        """
        if not self.main_tab.currentIndex():
            self.get_disk_properties()

        elif self.main_tab.currentIndex() == 1:
            self.get_share_properties()

    def get_disk_properties(self):
        """ get the number and size of the selected """
        readable = common.convert_bytes
        rows = self.selected_rows
        total_size = 0
        for index in rows:
            file = self.path_from_row(index)
            try:
                total_size += os.path.getsize(file)
            except FileNotFoundError:
                pass
        if rows:
            self.left_statusbar.setText(f"{len(rows)} selected, {readable(total_size)}")
        else:
            self.left_statusbar.setText("")

    def get_share_properties(self):
        """ get the number and size of the selected """
        readable = common.convert_bytes
        rows = self.share_selected
        total_size = 0
        for index in rows:
            name, f_exists, file_type, size = self.share_from_row(index)
            total_size += size
        if rows:
            self.left_statusbar.setText(f"{len(rows)} selected, {readable(total_size)}")
        else:
            self.left_statusbar.setText("")

    def update_stats(self):
        """
        update info about files on main window and on tray
        """

        self.disk_man.disk_stats_label.setText(f"Disk: {self.current_disk_name}, Files: {self.total_files}")

    def closeEvent(self, e):
        """
        minimize on close
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
        # show window
        self.showMaximized()

    def disk_context_menu(self, e):
        """
        external storage popup menu
        parameter e:
            contextMenu event
        assumes:
            self.tab_changed has been called
            self.table_view has been defined
        """
        if self.isDiskTableFocused:

            context = QMenu(self)
            # addAction(self, QIcon, str, PYQT_SLOT, shortcut: Union[QKeySequence, QKeySequence.StandardKey, str, int] = 0)
            context.addAction(self.open_icon, "Open", self.open_file)
            context.addSeparator()
            context.addAction(self.copy_icon, "Copy", self.copy, "Ctrl+C")
            context.addAction(self.cut_icon, "Cut", self.cut, "Ctrl+X")
            context.addSeparator()
            context.addAction(self.delete_icon, "Delete", self.delete_files)
            context.exec_(e.globalPos())

    def share_context_menu(self, e):
        """
        share files popup menu
        parameter e:
            contextMenu event
        assumes:
            self.share_man.share_table has been defined
        """
        if self.isShareTableFocused:
            context = QMenu(self)
            # addAction(self, QIcon, str, PYQT_SLOT, shortcut: Union[QKeySequence, QKeySequence.StandardKey, str, int] = 0)
            context.addAction(self.download_icon, "Download", self.download_clicked)
            context.addSeparator()
            context.addAction("Copy")
            context.addAction("Cut")
            context.addSeparator()
            context.addAction("Delete")
            context.exec_(e.globalPos())

    def contextMenuEvent(self, e):
        """
        window popup menu
        assumes:
            self.main_tab has been defined
        """
        if not self.main_tab.currentIndex():
            self.disk_context_menu(e)

        elif self.main_tab.currentIndex() == 1:
            self.share_context_menu(e)

    def keyPressEvent(self, e):
        """
        route key presses to their respective slots
        """
        try:
            if self.isDiskTableFocused:
                func = self.key_routes.get(e.key())
                if func:
                    func()
            elif self.isShareTableFocused:
                func = self.sharefiles_routes.get(e.key())
                if func:
                    func()
        except AttributeError:
            pass

    def on_startup(self, listdrives: Iterable[str]):
        """
        get disks and setup on startup
        """

        if listdrives:
            self.available_disks = set(listdrives)
            for disk in self.available_disks:
                self.set_path(disk)
            # simulate an insert
            self.set_events()
        else:
            self.disk_man.create_banner("Insert Disk")

    def set_events(self):
        """
        call on first disk insert
        """

        # call tab_changed whenever current tab changes
        self.disk_man.drives_tab.currentChanged.connect(self.tab_changed)
        # set event callbacks
        self.disk_man.search_input.textChanged.connect(self.search)

    def set_path(self, path: str):
        """
        update current folders and setup model/view
        """
        if self.disk_man.on_banner:
            self.disk_man.create_disk_win()
            self.set_events()

        folders = asfaUtils.get_folders(path)
        file_generators = [asfaUtils.get_files(folder) for folder in folders]
        self.disk_man.create_files_list(file_generators, path)
        # simulate tab changed
        self.tab_changed()
        # done once
        self.table_view.doubleClicked.connect(self.on_double_click)

    def on_disk_changes(self, listdrives: Iterable[str]):
        """
        respond to disk insert/eject
        """

        if listdrives:
            disks = set(listdrives)
            ejected = self.available_disks.difference(disks)
            inserted = disks.difference(self.available_disks)
            self.available_disks = disks
            if inserted:
                disk = inserted.pop()
                self.set_path(disk)
                self.tray.showMessage(f"asfa has detected Disk {disk}", "Transfer files here", self.app_icon)
            elif ejected:
                index = self.index_from_tabText(ejected.pop()[:2])
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

    def select_all(self):
        """ select all, Ctrl+A shortcut """
        try:
            if not self.main_tab.currentIndex():
                self.table_view.selectAll()
        except Exception:
            pass

    def focus_search_input(self):
        """ focus QLineEdit """
        try:
            index = self.main_tab.currentIndex()
            # if external storage or share files tab is selected
            if not index:
                self.disk_man.search_input.setFocus()
        except Exception:
            pass

    def search(self, search_txt):
        """
        change the search button icon and set the filter txt
        callback for QLineEdit textChanged event
        """

        if not self.main_tab.currentIndex():
            # search 2 characters and above
            if len(search_txt) > 1:
                self.files_model.setFilterRegExp(search_txt)
                self.disk_man.search_button.setIcon(self.cancel_icon)
                self.disk_man.search_button.clicked.connect(self.close_search)
            elif not search_txt:
                self.close_search()

    def close_search(self):
        """
        close a search and update the search button icon
        """

        self.disk_man.search_button.setIcon(self.disk_man.search_icon)
        self.disk_man.search_button.clicked.connect(self.on_search)
        self.disk_man.search_input.clear()
        self.files_model.setFilterRegExp("")

    def on_double_click(self, s: QModelIndex):
        """
        open a file on double-click
        """

        self._open_file(s)

    def _open_file(self, index: QModelIndex):
        """ open file at index by default app """
        try:
            if not self.main_tab.currentIndex():
                path = self.path_from_row(index)
                asfaUtils.start_file(path)
        except FileNotFoundError:
            self.inform(f"File not found!\n{path}")
            self.files_model.removeRow(index.row())

    def path_from_row(self, row: QModelIndex):
        """
        get data from the first and the second column of row
        join them and return full file path
        """

        row = row.row()
        dirname = self.files_model.data(self.files_model.index(row, 1))
        file = self.files_model.data(self.files_model.index(row, 0))
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

        if not self.main_tab.currentIndex():
            selected = self.selected_rows[::-1]
            if selected:
                confirmation = self.ask(f"Delete {len(selected)} selected file(s) permanently?\nNote: This cannot be undone!")
                # if confirmation is YES
                if confirmation == QMessageBox.Yes:
                    for index in selected:
                        path = self.path_from_row(index)
                        asfaUtils.delete_file(path)
                        self.files_model.removeRow(index.row())
                    self.update_stats()

    def open_file(self):
        """
        open last-selected file
        """

        try:
            index = self.selected_rows[-1]
            self._open_file(index)
        except IndexError:
            pass

    def _handle_transfer(self, dst, task="copy"):
        """ prepare transfer objects and enqueue them to manager """
        selected = self.selected_rows[::-1]
        dups_counter = 0
        for index in selected:
            src = self.path_from_row(index)
            if asfaUtils.file_exists(src, dst):
                self.worker_manager.duplicates.append(os.path.basename(src))
                dups_counter += 1
                continue
            transfer_worker = asfaUtils.Transfer(
                src, dst,
                os.path.getsize(src),
                model=self.files_model,
                indx=index, task=task
            )
            self.worker_manager.enqueue(transfer_worker)
        # if the selected exist in dst
        if dups_counter == len(selected):
            self.worker_manager.handle_dups()

    def copy(self):
        """
        copy files
        """

        if not self.main_tab.currentIndex() and not self.disk_man.on_banner:
            try:
                # get the dst from dialog
                dst = str(QFileDialog.getExistingDirectory(self, "Copy selected items to..."))
                # if dir selected
                if dst:
                    self.worker_manager.transfer_to.setText(f"Copying to '{dst}'")
                    self._handle_transfer(dst)

            except AttributeError as e:
                # self.inform("Insert Disk! Ascertain that a disk is mounted.")
                print("[Error Copying]", e)

    def cut(self):
        """
        cut files
        """

        if not self.main_tab.currentIndex() and not self.disk_man.on_banner:
            try:
                # get the dst from dialog
                dst = str(QFileDialog.getExistingDirectory(self, "Move selected items to..."))
                # if dir selected
                if dst:
                    self.worker_manager.transfer_to.setText(f"Moving to '{dst}'")
                    # model is needed when moving files
                    self._handle_transfer(dst, task="move")

            except AttributeError as e:
                # self.inform("Insert Disk! Ascertain that a disk is mounted.")
                print("[Error Moving]", e)

    def folder_transfer(self):
        """ handles transfers initiated from tray menu """
        try:
            src, dst, operation, isRecursive = self._get_menu_selections()
            if all((src, dst, operation, isRecursive)):
                dst = os.path.expanduser(f"~\\{dst}")
                if operation == "Copy":
                    self.worker_manager.transfer_to.setText(f"Copying to '{dst}'")
                    self._copy_folder(src, dst, recurse=isRecursive)
                else:
                    self.worker_manager.transfer_to.setText(f"Moving to '{dst}'")
                    self._copy_folder(src, dst, recurse=isRecursive)

        except AttributeError:
            pass

    def _get_menu_selections(self):
        """ get the src, dst, op, recurse from menu """
        dst = self.tray_menu.to_folder.currentText()
        src = self.tray_menu.from_folder.currentText()
        operation = self.tray_menu.copy_cut.currentText()
        recursive = self.tray_menu.recurse_folders.isChecked()
        return src, dst, operation, recursive

    def _copy_folder(self, src_folder: str, dst_folder: str, recurse=True):
        """ copy folder recursively """
        dst_name = os.path.basename(src_folder) or "Removable Disk"
        dst = os.path.join(dst_folder, dst_name)
        if not os.path.exists(dst):
            os.mkdir(dst)
        sorted_items = asfaUtils.get_files_folders(src_folder)
        for item in sorted_items:
            if os.path.isfile(item):
                # pass model and indexes
                transfer_worker = asfaUtils.Transfer(
                    item, dst,
                    os.path.getsize(item)
                )
                self.worker_manager.enqueue(transfer_worker)
            elif os.path.isdir(item) and recurse:
                # recurse
                self._copy_folder(item, dst)

    # ----------------------- Let's start sharing files ---------------------------------------

    def back_to_folder(self):
        """ go back a folder """
        try:
            if len(self.server_browser.browser_history) > 1:
                # keep home dir for refreshing
                self.server_browser.browser_history.pop()
            # if len(self.server_browser.browser_history) != 1:
            folder = self.server_browser.browser_history[-1]
            self.update_shared_files(path=folder)
            # print("-->", folder, len(self.server_browser.browser_history))
        except IndexError:
            pass

    def update_shared_files(self, path=None):
        """
        FTP: fetch files from the specified path
        if path is None, refresh the cwd
        """

        self.server_browser.updateDir(path)
        generator = self.server_browser.getFilesList()
        self.share_man.add_files(generator)
        open_dir = "Home:/" + "/".join(self.server_browser.browser_history)
        self.share_man.show_current_folder.setText(open_dir)
        # update the selection model for the new path
        self.share_man.share_table.selectionModel().selectionChanged.connect(self.get_properties)
        self.get_properties()

    @property
    def share_selected(self) -> Iterable[QModelIndex]:
        """ get selected files in share window """
        selection_model = self.share_man.share_table.selectionModel()
        return selection_model.selectedRows()

    def share_from_row(self, row: QModelIndex):
        """ return a row as a tuple """
        row = row.row()
        model = self.share_man.share_model
        filename = model.data(model.index(row, 0), role=Qt.UserRole)
        status = model.data(model.index(row, 1), role=Qt.UserRole)
        item_type = model.data(model.index(row, 2), role=Qt.UserRole)
        size = model.data(model.index(row, 3), role=Qt.UserRole)
        return filename, status, item_type, size

    def _change_icon(self, index, code):
        """ change status code of `index` hence its icon """
        self.share_man.share_model.layoutAboutToBeChanged.emit()
        name, f_exists, file_type, size = self.share_from_row(index)
        self.share_man.share_model.dataList[index.row()] = (name, code, file_type, size)
        self.share_man.share_model.layoutChanged.emit()

    def download_clicked(self):
        """
        1. get selected files
        2. loop passing each file to download worker
        """

        selected = self.share_selected
        if selected:
            self.main_tab.insertTab(2, self.downloads_win, "Downloads")
        for index in selected:
            filename, f_exists, file_type, size = self.share_from_row(index)
            cwdir = "/".join(self.server_browser.browser_history)
            downloads_folder = os.path.expanduser("~\\Downloads")
            # skip files that exist
            if not os.path.exists(os.path.join(downloads_folder, filename)):
                self._change_icon(index, 2)
                w = asfaDownloads.Worker(filename, cwdir, size, indx=index)
                # -> function to change file status hence its icon
                w.signals.finished.connect(lambda job_id, x: self._change_icon(x, 1))
                # w.signals.error.connect(self.display_result)

                self.downloads_win.workers.enqueue(w)

    def share_double_click(self, index: QModelIndex):
        """ respond to share table double-click """
        self.handle_share_open(index)

    def share_open_file(self):
        """ slot for `enter` button """
        try:
            index = self.share_selected[-1]
            self.handle_share_open(index)
        except IndexError:
            pass

    def handle_share_open(self, index):
        filename, f_exists, file_type, size = self.share_from_row(index)
        downloads_folder = os.path.expanduser("~\\Downloads")
        if file_type == "Folder":
            self.update_shared_files(path=filename)
        else:
            # open files that exist
            path = os.path.join(downloads_folder, filename)
            if os.path.exists(path):
                asfaUtils.start_file(path)
            else:
                self.download_clicked()

    def update_new_user(self, user: tuple):
        """
        receive new users and add their details to dropdown menu
        """
        if user not in self.those_online:
            username, address = user
            # the IP address for the remote machine
            self.server_browser.updateHost(("192.168.43.28", 3000))
            self.share_man.add_files(self.server_browser.getFilesList())
            self.those_online.add(user)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    # app.setStyleSheet(QSS)

    def close_win():

        # c.tray.hide()
        c.usb_thread.close()
        c.server.stopServer()
        app.quit()
        sys.exit(0)

    c = Controller()
    c.tray_menu.quit.clicked.connect(close_win)

    # memory usage in MBs
    memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1048576
    print(f"[MEMORY USED] : {memory_usage} MB")

    sys.exit(app.exec_())
