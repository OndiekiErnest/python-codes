__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"

from typing import List
from functools import wraps
from types import MethodType
from network import server, browser
import os
from qss import QSS
import asfaUtils
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
        # declare icons
        self.video_icon = QIcon("data\\videos.png")
        self.doc_icon = QIcon("data\\doc.png")
        self.audio_icon = QIcon("data\\audio.png")
        self.image_icon = QIcon("data\\images.png")

        # header row
        self.disks_dropdown = QComboBox(self)
        self.disks_dropdown.currentTextChanged.connect(self.update_disk_folders)
        header_row = QWidgetAction(self)
        header_row.setDefaultWidget(self.disks_dropdown)
        self.addAction(header_row)

        # choice row
        choices_holder = QWidget(self)
        hlayout = QVBoxLayout(self)

        self.copy_cut = QComboBox(self)
        self.copy_cut.addItems(("Copy", "Cut"))
        self.copy_cut.currentTextChanged.connect(self.update_text)
        from_label = QLabel("From:", self)
        self.from_folder = QComboBox(self)
        to_label = QLabel("To:", self)
        self.to_folder = QComboBox(self)
        self.to_folder.addItems(("Documents", "Pictures", "Videos", "Music"))
        self.recurse_folders = QCheckBox("Transfer its folders", self)
        self.recurse_folders.setChecked(1)

        hlayout.addWidget(self.copy_cut)
        hlayout.addWidget(from_label)
        hlayout.addWidget(self.from_folder)
        hlayout.addWidget(to_label)
        hlayout.addWidget(self.to_folder)
        hlayout.addWidget(self.recurse_folders)
        choices_holder.setLayout(hlayout)
        choices_row = QWidgetAction(self)
        choices_row.setDefaultWidget(choices_holder)
        self.addAction(choices_row)

        self.videos_action = QAction(self.video_icon, "Copy all Videos")
        self.doc_action = QAction(self.doc_icon, "Copy all Documents")
        self.audio_action = QAction(self.audio_icon, "Copy all Audio")
        self.images_action = QAction(self.image_icon, "Copy all Images")
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

    def update_text(self, choice):
        try:
            self.videos_action.setText(f"{choice} all Videos")
            self.doc_action.setText(f"{choice} all Documents")
            self.audio_action.setText(f"{choice} all Audio")
            self.images_action.setText(f"{choice} all Images")
            self.selected = choice
        except AttributeError:
            pass

    def update_disk_folders(self, disk):
        self.from_folder.clear()
        if disk:
            self.from_folder.addItems(asfaUtils.get_folders(disk))


class DuplicatesWindow(QWidget):

    def __init__(self, files: tuple, *args):
        super().__init__(*args)
        self.setWindowTitle("Feedback - asfa")
        self.setFixedSize(400, 150)

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
        super().__init__(*args)
        self.setWindowTitle("Transfering - asfa")
        self.setFixedSize(400, 150)

        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        self.cancel_transfer = QPushButton("Cancel", self)
        btn_layout.addWidget(self.cancel_transfer, alignment=Qt.AlignRight)
        self.transfer_to = QLabel("Transfering to:", self)
        self.percentage_progress = QLabel("70%", self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(0)
        self.remaining_time = QLabel("0 minutes remaining", self)
        self.remaining_files = QLabel("0 Files Remaining", self)
        main_layout.addWidget(self.transfer_to)
        main_layout.addWidget(self.percentage_progress)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.remaining_time)
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
    _workers_etime = {}
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
        print("Multithreading with maximum %d threads" % self.max_threads)
        self.cancel_transfer.clicked.connect(self.cancel)

    def enqueue(self, worker):
        """ Enqueue a worker to run (at some point) by passing it to the QThreadPool """
        worker.signals.progress.connect(self.receive_progress)
        worker.signals.finished.connect(self.done)
        worker.signals.etime.connect(self.estimate_time)
        worker.signals.transferred.connect(self.receive_transferred)
        self.files_threadpool.start(worker)
        self._active_workers[worker.job_id] = worker
        self.total_workers += 1
        self.total_size += worker.size
        self.show()

    def estimate_time(self, job_id, etime):
        self._workers_etime[job_id] = etime

    def receive_progress(self, job_id, progress):
        self._workers_progress[job_id] = progress

    def receive_transferred(self, job_id, size):
        self._transferred[job_id] = size

    def calculate_rem_time(self):
        """ Calculate total progress """
        if not self._workers_progress:
            return (0, 0)
        rem_time = sum(v for v in self._workers_etime.values())
        return divmod(rem_time, 60)

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
        mins, sec = self.calculate_rem_time()
        transferred = self.calculate_transferred()
        rem_size = asfaUtils.convert_bytes(self.total_size - transferred)
        transfering = min(self.max_threads, len(self._active_workers))
        rem_files = max(0, len(self._active_workers) - self.max_threads)

        self.progress_bar.setValue(progress)
        self.percentage_progress.setText(f"{progress}%")
        self.remaining_files.setText(f"{transfering} transfering ({asfaUtils.convert_bytes(transferred)}), {rem_files} remaining ({rem_size})")
        if mins:
            self.remaining_time.setText(f"About {int(mins)} m {int(sec)} s remaining")
        else:
            if sec:
                self.remaining_time.setText(f"About {int(sec)} s remaining")
            else:
                self.remaining_time.setText("About a few seconds remaining")

    def done(self, job_id):
        """ Remove workers when all jobs are done 100% """
        # avoid KeyError
        if self._active_workers:
            del self._active_workers[job_id]
        if all(v == 100 for v in self._workers_progress.values()) and not (self._active_workers):
            self._workers_progress.clear()
            self._workers_etime.clear()
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


class DiskManager():
    """
        disk window manager
    """

    def __init__(self, parent):
        # window icons
        self.disk_management_win = QWidget()
        self.main_layout = QVBoxLayout()
        self.search_icon = QIcon("data\\search.png")
        self.available_file_types = set()
        self.on_banner = 0
        # self.main_layout = None
        self.on_search_shortcut = QShortcut(QKeySequence("Ctrl+F"), parent)
        self.select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), parent)
        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), parent)
        self.cut_shortcut = QShortcut(QKeySequence("Ctrl+X"), parent)

    def create_disk_win(self):
        """
            create the window to hold widgets
            that will go in the disk management tab
        """

        asfaUtils.close_window(self.main_layout)
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
        self.on_banner = 0

    def create_files_list(self, generators: list, tab_name):
        """
            create a table to show files in different folders
        """

        # model = TableModel(generators, ("Name", "File Path", "Type", "Size"))
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
                # get only the file extension, sets remove duplicates
                self.available_file_types.add(row[2].split(" ")[0])

        # print(model.rowCount())
        filter_proxy_model = SortFilterModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(-1)

        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(0)
        # select all Ctrl+A shortcut
        self.select_all_shortcut.activated.connect(self.table.selectAll)
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

    def create_banner(self, msg: str):
        """
            create a banner to communicate to the user
        """

        asfaUtils.close_window(self.main_layout)
        self.msg_label = QLabel(parent=self.disk_management_win)
        # self.close_msg_button.clicked.connect(self.create_disk_win)
        self.msg_label.setText(msg)
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.msg_label)
        self.disk_management_win.setLayout(self.main_layout)
        # banner flag
        self.on_banner = 1


class ShareManager():
    """
        share window manager
    """

    def __init__(self, parent):
        # window icons

        self.file_share_win = QWidget(parent)
        self.main_layout = QVBoxLayout()
        self.search_icon = QIcon("data\\search.png")
        self.on_banner = 0
        # self.main_layout = None

    def create_share_win(self):
        """
            create the window for share files tab
        """

        asfaUtils.close_window(self.main_layout)
        hlayout = QHBoxLayout()
        # use v layout for this widget
        self.file_share_win.setLayout(self.main_layout)
        dirchooser_btn = QPushButton("Browse", self.file_share_win)
        dirchooser_btn.clicked.connect(self.dir_chooser)
        self.share_stats_label = QLabel()
        self.server_state = QLabel("Server not set")
        hlayout.addWidget(dirchooser_btn)
        hlayout.addWidget(self.share_stats_label)
        hlayout.addStretch()
        hlayout.addWidget(self.server_state)
        # nest an inner layout
        self.main_layout.addLayout(hlayout)
        # create table for files display

        self.share_table = QTableView()
        self.share_table.clicked.connect(self.on_click)
        self.main_layout.addWidget(self.share_table)
        self.on_banner = 0

    def dir_chooser(self):
        shared_folder = str(QFileDialog.getExistingDirectory(self.file_share_win, "asfa - Choose folder"))
        if shared_folder:
            self.share_stats_label.setText(shared_folder)

    def on_click(self, index):
        # print(index.row(), index.data())
        pass

    def add_files(self, files: list):
        """
            create a table to show shared files
        """

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Name", "Type", "Size"])

        for row in files:
            name = QStandardItem(row[0])
            name.setToolTip(row[0])
            row_type = QStandardItem(row[1])
            row_type.setTextAlignment(Qt.AlignCenter)
            size_column = QStandardItem(asfaUtils.convert_bytes(row[2]))
            size_column.setTextAlignment(Qt.AlignCenter)

            model.appendRow((name, row_type, size_column))
        # print(model.rowCount())
        filter_proxy_model = ShareFilesModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(-1)

        self.share_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.share_table.verticalHeader().setVisible(0)
        self.share_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.share_table.setModel(filter_proxy_model)
        self.share_table.setSortingEnabled(1)
        self.share_table.setShowGrid(0)
        # self.share_table.setAlternatingRowColors(1)
        self.share_table.setEditTriggers(self.share_table.NoEditTriggers)

    def create_banner(self, msg: str):
        """
            create a banner to communicate to the user
        """

        asfaUtils.close_window(self.main_layout)
        self.msg_label = QLabel(parent=self.disk_management_win)
        # self.close_msg_button.clicked.connect(self.create_disk_win)
        self.msg_label.setText(msg)
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.msg_label)
        self.disk_management_win.setLayout(self.main_layout)
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
        # set qss style
        # self.main_tab.setStyleSheet("font: 16pts")
        # modify the font
        font = self.main_tab.font()
        font.setPointSize(14)
        self.main_tab.setFont(font)
        # ; border-radius: 15px; border: 2px solid black
        # create the window to hold widgets that will go in the first tab
        self.disk_man = DiskManager(self)
        # self.disk_man.create_banner("Insert Disk")
        self.main_tab.insertTab(0, self.disk_man.disk_management_win, "External Storage")
        # create the first tab
        self.disk_man.create_disk_win()
        # for the second tab
        self.share_man = ShareManager(self)
        self.share_man.create_share_win()
        self.main_tab.addTab(self.share_man.file_share_win, "Share Files")
        # create downloads tab
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
        # self.folders = []
        self.available_disks = set()
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.app_icon)
        self.tray.setToolTip("asfa")

        self.server_browser = browser.ServerBrowser()
        self.server_browser.updateHost(("127.0.0.1", 3000))
        self.server = server.Server()
        self.server.setSharedDirectory(os.path.expanduser("~\\Desktop"))
        self.server.start()
        self.share_man.add_files(self.server_browser.getFilesList())

        self.tray_menu = TrayMenu(self)
        self.tray_menu.create_all()
        self.tray_menu.videos_action.triggered.connect(self.folder_transfer)
        self.tray_menu.more.clicked.connect(self.show_main_window)
        self.tray.setContextMenu(self.tray_menu)
        self.disk_man.copy_shortcut.activated.connect(self.copy)
        self.disk_man.cut_shortcut.activated.connect(self.cut)
        # set focus shortcut
        self.disk_man.on_search_shortcut.activated.connect(self.focus_search_input)

        # self.set_path(os.path.expanduser("~\\Downloads"))
        self.worker_manager = WorkerManager()
        self.worker_manager.setWindowIcon(self.app_icon)
        # start the usb listener
        self.threadpool = QThreadPool()
        self.usb_thread = asfaUtils.DeviceListener()
        self.on_startup(self.usb_thread.disks)
        self.usb_thread.signals.on_change.connect(self.on_disk_changes)
        self.usb_thread.signals.error.connect(self.disk_man.create_banner)
        self.threadpool.start(self.usb_thread)
        self.show()
        # self.tray.show()
        # self.tray.showMessage("asfa is running here", "Right-click the icon for more options", self.app_icon)
        self.key_routes = {Qt.Key_Enter: self.open_file, Qt.Key_Return: self.open_file, Qt.Key_Delete: self.delete_files}

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
        self.model = self.table_view.model()
        self.selection_model = self.table_view.selectionModel()
        self.selection_model.selectionChanged.connect(self.get_properties)
        # show stats per disk
        self.update_stats()
        self.get_properties(None, None)

    def share_tab(self, func):
        """
        share files tab decorator
        modifies functions that run only when share files tab is selected
        assumes:
            self.main_tab has been defined
        """
        def inner(*args, **kwargs):
            # if current index is share files tab
            if self.main_tab.currentIndex() == 1:
                return func(*args, **kwargs)
        return inner

    def settings_tab(self, func):
        """
        settings tab decorator
        modifies functions that run only when settings tab is selected
        assumes:
            self.main_tab has been defined
        """
        def inner(*args, **kwargs):
            # if current index is share files tab
            if self.main_tab.currentIndex() == 2:
                return func(*args, **kwargs)
        return inner

    @property
    def selected_rows(self) -> List[QModelIndex]:
        """
        get the currently selected rows
        """

        return tuple(self.selection_model.selectedRows())

    @property
    def total_files(self) -> int:
        """
        get all files
        """

        return self.model.rowCount()

    @property
    def isDiskTableFocused(self) -> bool:
        """
        check if table view is under mouse and focused
        """

        return (self.table_view.underMouse() and self.table_view.hasFocus())

    @property
    def isShareTableFocused(self):
        table = self.share_man.share_table
        return (table.underMouse() and table.hasFocus())

    def get_properties(self, selected, deselected):
        """
        get the total size of all the selected files
        """
        rows = self.selected_rows
        total_size = 0
        for row in rows:
            file = self.path_from_row(row)
            total_size += os.path.getsize(file)
        if total_size:
            self.left_statusbar.setText(f"{len(rows)} selected, {asfaUtils.convert_bytes(total_size)}")
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
        self.tray_menu.disks_dropdown.clear()
        self.tray_menu.disks_dropdown.addItems(self.available_disks)
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
            context.addAction("Download")
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
        except AttributeError:
            pass

    def on_startup(self, listdrives):
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

    def on_disk_changes(self, listdrives):
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
                self.tray_menu.disks_dropdown.clear()
                self.tray_menu.disks_dropdown.addItems(self.available_disks)
                self.tray.showMessage(f"asfa has detected Disk {disk}", "Transfer files here", self.app_icon)
            elif ejected:
                self.tray_menu.disks_dropdown.clear()
                self.tray_menu.disks_dropdown.addItems(self.available_disks)
                index = self.index_from_tabText(ejected.pop()[:2])
                self.disk_man.close_files_list(index)
        else:
            self.available_disks = set()
            self.disk_man.create_banner("Insert Disk")
            self.tray_menu.disks_dropdown.clear()

    def on_search(self):
        """
        slot for search button
        """

        string = self.disk_man.search_input.text()
        self.search(string)

    def focus_search_input(self):
        """ focus QLineEdit """
        index = self.main_tab.currentIndex()
        # if external storage or share files tab is selected
        if not index: # or index == 1:
            self.disk_man.search_input.setFocus()

    def search(self, search_txt):
        """
        change the search button icon and set the filter txt
        callback for QLineEdit textChanged event
        """

        if not self.main_tab.currentIndex():
            # search 2 characters and above
            if len(search_txt) > 1:
                self.model.setFilterRegExp(search_txt)
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
        self.model.setFilterRegExp("")

    def on_double_click(self, s: QModelIndex):
        """
        open a file on double-click
        """

        if not self.main_tab.currentIndex():
            path = self.path_from_row(s)
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

        if not self.main_tab.currentIndex():
            selected = self.selected_rows[::-1]
            confirmation = self.ask(f"Delete {len(selected)} selected file(s) permanently?")
            # if confirmation is YES
            if confirmation == 16384:
                for index in selected:
                    path = self.path_from_row(index)
                    asfaUtils.delete_file(path)
                    self.model.removeRow(index.row())
                self.update_stats()

    def open_file(self):
        """
        open last-selected file
        """

        if not self.main_tab.currentIndex():
            path = self.path_from_row(self.selected_rows[-1])
            asfaUtils.start_file(path)

    def copy(self):
        """
        copy files
        """

        if not self.main_tab.currentIndex():
            try:
                # get the dst from dialog
                dst = str(QFileDialog.getExistingDirectory(self, "Copy to..."))
                # if dir selected
                if dst:
                    self.worker_manager.transfer_to.setText(f"Copying to {dst}")
                    selected = self.selected_rows
                    dups_counter = 0
                    for index in selected:
                        src = self.path_from_row(index)
                        if asfaUtils.file_exists(src, dst):
                            self.worker_manager.duplicates.append(src)
                            dups_counter += 1
                            continue
                        transfer_worker = asfaUtils.Transfer(src, dst, os.path.getsize(src))
                        self.worker_manager.enqueue(transfer_worker)
                    # if the selected exist in dst
                    if dups_counter == len(selected):
                        self.worker_manager.handle_dups()

            except AttributeError as e:
                # self.inform("Insert Disk! Ascertain that a disk is mounted.")
                print("[Error Copying]", e)

    def cut(self):
        """
        cut files
        """

        if not self.main_tab.currentIndex():
            try:
                # get the dst from dialog
                dst = str(QFileDialog.getExistingDirectory(self, "Move to..."))
                # if dir selected
                if dst:
                    self.worker_manager.transfer_to.setText(f"Moving to {os.path.basename(dst)}")
                    selected = self.selected_rows[::-1]
                    dups_counter = 0
                    for index in selected:
                        src = self.path_from_row(index)
                        if asfaUtils.file_exists(src, dst):
                            self.worker_manager.duplicates.append(src)
                            dups_counter += 1
                            continue
                        transfer_worker = asfaUtils.Transfer(src, dst, os.path.getsize(src), model=self.model, indx=index)
                        self.worker_manager.enqueue(transfer_worker)
                    # if all selected exist in dst
                    if dups_counter == len(selected):
                        self.worker_manager.handle_dups()

            except AttributeError as e:
                # self.inform("Insert Disk! Ascertain that a disk is mounted.")
                print("[Error Moving]", e)

    def folder_transfer(self):
        """ handles transfers initiated from tray menu """
        try:
            src, dst, operation, isRecursive = self._get_menu_selections()
            dst = os.path.expanduser(f"~\\{dst}")
            if operation == "Copy":
                self._copy_folder(src, dst, recurse=isRecursive)
            else:
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
        dst = os.path.join(dst_folder, os.path.basename(src_folder))
        if not os.path.exists(dst):
            os.mkdir(dst)
        sorted_items = asfaUtils.get_files_folders(src_folder)
        for item in sorted_items:
            if os.path.isfile(item):
                # transfer file
                print(item, "->", dst)
            elif os.path.isdir(item) and recurse:
                # recurse
                self._copy_folder(item, dst)


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
