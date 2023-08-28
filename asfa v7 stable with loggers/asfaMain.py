__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


from typing import Iterable, Generator
from network import server, browser
import common
import os
from qss import QSS
from config import Settings
from serverSettings import ServerSettingsWindow
from customWidgets import (
    Qt, PathEdit, QTabWidget, TabWidget,
    QLineEdit, QFileDialog, QPushButton, pyqtSignal,
    PasswordEdit, QHBoxLayout, QSize,
)
import asfaUtils
import asfaDownloads
from asfaModel import DiskFilesModel, SortFilterModel, ShareFilesModel
from PyQt5.QtCore import (
    QThreadPool, QModelIndex, QTimer
)
from PyQt5.QtGui import (
    QIcon,
    QStandardItemModel,
    QKeySequence
)
from PyQt5.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QWidgetAction,
    QAbstractItemView,
    QHeaderView,
    QLabel, QWidget,
    QShortcut, QListWidget,
    QMenu,
    QComboBox,
    QGroupBox,
    QVBoxLayout, QGridLayout,
    QFormLayout,
    QTableView, QRadioButton,
    QCheckBox, QProgressBar,
    QMessageBox
)


LAST_KNOWN_DIR = os.path.expanduser(f"~{common.OS_SEP}Documents")


def get_directory(parent, caption):
    """ get folder, return None on cancel """
    folder = os.path.normpath(QFileDialog.getExistingDirectory(
        parent, caption=f"{caption}",
        directory=LAST_KNOWN_DIR,
    ))
    if folder != ".":
        return folder


class TrayMenu(QMenu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("trayMenu")

        # header row
        self.to_transfer_win = QPushButton("Transfer folders")
        self.to_transfer_win.setObjectName("trayTransferBtn")
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
        self.quit.setObjectName("trayQuitBtn")
        self.more = QPushButton("More")
        self.more.setObjectName("trayMoreBtn")
        hlayout.addWidget(self.more)
        hlayout.addWidget(self.quit)
        self.abuttons_holder.setLayout(hlayout)
        self.last_action = QWidgetAction(self)
        self.last_action.setDefaultWidget(self.abuttons_holder)
        self.addAction(self.last_action)


class DuplicatesWindow(QWidget):
    """
    window for displaying duplicate files
    inherits:
        QWidget
    """

    def __init__(self, files: Iterable[str], *args):

        super().__init__(*args)
        self.setObjectName("duplicatesWindow")
        self.setWindowTitle("Feedback - asfa")
        self.setFixedSize(450, 200)

        vlayout = QVBoxLayout()

        details_label = QLabel("These files already exist in the destination folder:", self)
        details_label.setObjectName("duplicatesTitle")
        list_widget = QListWidget(self)
        list_widget.setObjectName("duplicatesListWidget")
        list_widget.addItems(files)
        ok_btn = QPushButton("OK", self)
        ok_btn.setObjectName("duplicatesOkBtn")
        ok_btn.clicked.connect(self.deleteLater)

        vlayout.addWidget(details_label)
        vlayout.addWidget(list_widget)
        vlayout.addWidget(ok_btn, alignment=Qt.AlignRight)
        self.setLayout(vlayout)


class TransferWindow(QWidget):
    """
    window for displaying transfer progress
    inherits:
        QWidget
    """

    def __init__(self, *args):

        super().__init__(*args)
        self.setObjectName("transferWin")
        self.setWindowTitle("Transfering - asfa")
        self.setFixedSize(400, 150)

        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        self.cancel_transfer = QPushButton("Cancel")
        self.cancel_transfer.setObjectName("transferCancelBtn")
        btn_layout.addWidget(self.cancel_transfer, alignment=Qt.AlignRight)
        self.transfer_to = QLabel("Transfering to:")
        self.transfer_to.setObjectName("transferTo")
        self.percentage_progress = QLabel("0%")
        self.percentage_progress.setObjectName("transferPercentage")
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("transferProgressb")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(0)
        self.remaining_files = QLabel("0 Files Remaining", self)
        self.remaining_files.setObjectName("transferRem")

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
        # create a threadpool for workers
        self.files_threadpool = QThreadPool()
        self.files_threadpool.setMaxThreadCount(2)
        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.refresh_progress)
        self.timer.start()
        self.total_workers = 0
        self.total_size = 0
        self.duplicates = []
        asfaUtils.utils_logger.debug(f"Can transfer {self.files_threadpool.maxThreadCount()} files at a time")
        self.cancel_transfer.clicked.connect(self.cancel)

    def enqueue(self, worker: asfaUtils.Transfer):
        """ Enqueue a worker to run (at some point) by passing it to the QThreadPool """

        worker.signals.progress.connect(self.receive_progress)
        worker.signals.finished.connect(self.done)
        worker.signals.transferred.connect(self.receive_transferred)
        worker.signals.duplicate.connect(self.receive_dups)
        self._active_workers[worker.job_id] = worker
        self.total_workers += 1
        self.total_size += worker.size
        self.files_threadpool.start(worker)

        asfaUtils.utils_logger.debug(f"Total size {self.total_size} Bytes")
        self.show()

    def receive_progress(self, job_id, progress):
        self._workers_progress[job_id] = progress

    def receive_transferred(self, job_id, size):
        self._transferred[job_id] = size

    def receive_dups(self, file):
        self.duplicates.append(file)

    def calculate_progress(self):
        """ Calculate total progress """
        if not self._workers_progress or not self.total_workers:
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
        # self.hide()

    def handle_dups(self):
        if self.duplicates:
            self.w = DuplicatesWindow(self.duplicates)
            self.w.setWindowIcon(self.windowIcon())
            self.duplicates.clear()
            self.w.show()


class FolderTransferWin(QWidget):
    """
    create a window to popup when a flash-disk is inserted
    """

    def __init__(self, tray, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("folderPopup")
        # self.setMinimumSize(600, 300)
        self.setWindowTitle("Quick Transfer - asfa")

        self.tray_obj = tray
        self.loaded_settings = settings
        disk_name = self.loaded_settings.choices.get("disk")

        # define layouts
        self.form_layout = QFormLayout()
        self.left_v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()
        self.grid_layout = QGridLayout()
        # define groupboxes
        self.right_group = QGroupBox("Select file extensions to skip")
        self.right_group.setObjectName("extensionsGroup")
        self.bottom_left_group = QGroupBox("More options")
        self.bottom_left_group.setObjectName("optionsGroup")

        self.copy_flag = QRadioButton("Copy")
        self.copy_flag.setChecked(1)
        self.copy_flag.clicked.connect(self.vary_remember_disk_states)
        self.move_flag = QRadioButton("Cut")
        self.move_flag.clicked.connect(self.vary_remember_disk_states)
        self.recurse = QCheckBox("Transfer source sub-folders")
        self.recurse.setChecked(1)
        self.remember_disk_option = QCheckBox("Remember these choices (for this disk only)")
        self.remember_disk_option.setToolTip("""Attempt similar file transfer automatically
the next time you insert this disk.""")
        self.remember_disk_option.setDisabled(True)
        self.ok_button = QPushButton("OK")

        # nest layouts and set the main one to the main window
        self.h_layout.addLayout(self.left_v_layout)
        self.h_layout.addWidget(self.right_group)
        self.right_group.setLayout(self.grid_layout)
        self.setLayout(self.h_layout)

        self.create_first_column()
        if disk_name and os.path.exists(disk_name):
            self.populate_from_settings(settings)

    def create_first_column(self):
        left_title = QLabel("Choose folder to transfer:")
        self.transfer_from_folder_input = PathEdit("Choose a folder to transfer from")
        self.transfer_from_folder_size = QLabel()
        self.transfer_from_folder_input.setPlaceholderText("Source folder")
        self.transfer_from_folder_input.textChanged.connect(self.get_ext)

        self.transfer_to_folder_input = PathEdit("Choose a folder to transfer to")
        self.transfer_to_folder_input.setPlaceholderText("Destination folder")
        self.transfer_to_folder_input.textChanged.connect(self.vary_remember_disk_states)

        # dir chooser section
        first_row_layout = QHBoxLayout()
        first_row_layout.addWidget(self.transfer_from_folder_input)
        first_row_layout.addWidget(self.transfer_from_folder_size)
        self.form_layout.addRow("From", first_row_layout)
        self.form_layout.addRow("To", self.transfer_to_folder_input)

        # more settings group
        more_v_layout = QVBoxLayout()
        self.bottom_left_group.setLayout(more_v_layout)
        more_v_layout.addWidget(self.copy_flag)
        more_v_layout.addWidget(self.move_flag)
        more_v_layout.addWidget(self.recurse)
        more_v_layout.addWidget(self.remember_disk_option)

        self.left_v_layout.addWidget(left_title, alignment=Qt.AlignTop)
        self.left_v_layout.addLayout(self.form_layout)
        self.left_v_layout.addWidget(self.bottom_left_group)
        self.left_v_layout.addWidget(self.ok_button, alignment=Qt.AlignRight)

    def get_ext(self, folder):
        """ thread getting of exts """
        # remove the previous checkboxes
        asfaUtils.close_window(self.grid_layout)
        self.ext_thread = asfaUtils.Thread(asfaUtils.get_ext_recursive, folder)
        self.ext_thread.results.connect(self.create_last_column)
        self.ext_thread.start()
        self.vary_remember_disk_states()

    def vary_remember_disk_states(self):
        """ enable remember widget if path is removable and copy is checked """
        from_path = self.transfer_from_folder_input.text()[:3]
        to_path = self.transfer_to_folder_input.text()[:3]
        if (asfaUtils.isRemovable(from_path) or asfaUtils.isRemovable(to_path)) and self.copy_flag.isChecked():
            self.remember_disk_option.setEnabled(True)
        else:
            self.remember_disk_option.setChecked(False)
            self.remember_disk_option.setDisabled(True)

    def create_last_column(self, exts_size: Iterable):
        """ create checkboxes for file extensions available in dir """
        row, col = 0, 0
        folder_size, exts = exts_size
        data_len = len(exts)
        col_size = 5 if data_len > 25 else 3
        for r in range(data_len):
            try:
                self.grid_layout.addWidget(QCheckBox(exts[r]), row, col)
                col += 1
                if col == col_size:
                    row, col = row + 1, 0
            except IndexError:
                break
        self.transfer_from_folder_size.setText(f"({common.convert_bytes(folder_size)})")

    def get_selections(self):
        """ return: source_folder, dest_folder, copy, recurse, save_selection, ignore_patterns """
        source_folder = self.transfer_from_folder_input.text()
        dest_folder = self.transfer_to_folder_input.text()
        # move_flag and copy_flag are tied
        operation = self.copy_flag.isChecked()
        recurse = self.recurse.isChecked()
        save_selection = self.remember_disk_option.isChecked()

        item_at = self.grid_layout.itemAt
        total_widgets = self.grid_layout.count()
        ignore_patterns = {item_at(i).widget().text() for i in range(total_widgets) if item_at(i).widget().isChecked()}

        return source_folder, dest_folder, operation, recurse, save_selection, ignore_patterns

    def populate_from_settings(self, settings):
        self.transfer_from_folder_input.setText(settings.choices.get("source_folder", ""))
        self.transfer_to_folder_input.setText(settings.choices.get("dest_folder", ""))
        # move_flag and copy_flag are tied
        copy = settings.choices.get("copy", False)
        self.copy_flag.setChecked(copy)
        self.move_flag.setChecked(not copy)
        self.recurse.setChecked(settings.choices.get("recurse", False))
        self.remember_disk_option.setChecked(settings.choices.get("save", False))

    def closeEvent(self, e):
        """ on window close """
        self.tray_obj.show()
        self.hide()
        e.ignore()


class DiskManager(QWidget):
    """
        disk window widget
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("diskManager")
        # window icons
        self.main_layout = QVBoxLayout()
        self.search_icon = QIcon("data\\search.png")
        self.refresh_icon = QIcon("data\\refresh.png")
        self.on_banner = 0
        # self.main_layout = None
        self.on_search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
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
        self.refresh_files_btn = QPushButton()
        self.refresh_files_btn.setObjectName("refreshBtn")
        self.refresh_files_btn.setIcon(self.refresh_icon)
        self.refresh_files_btn.setToolTip("Get file changes")
        # create search area
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files here")
        input_layout = QHBoxLayout(self.search_input)
        input_layout.setContentsMargins(0, 0, 0, 0)
        self.search_button = QPushButton(self.search_input)
        self.search_button.setIcon(self.search_icon)
        self.search_button.setCursor(Qt.ArrowCursor)
        input_layout.addWidget(self.search_button, alignment=Qt.AlignVCenter | Qt.AlignRight)
        hlayout.addWidget(self.disk_stats_label)
        hlayout.addStretch()
        hlayout.addWidget(self.search_input)
        hlayout.addWidget(self.refresh_files_btn)
        # nest an inner layout
        self.main_layout.addLayout(hlayout)
        # create the inner vertical tab widget
        self.drives_tab = TabWidget()
        self.drives_tab.setMovable(1)
        self.drives_tab.setDocumentMode(1)
        self.main_layout.addWidget(self.drives_tab)
        self.on_banner = 0

    def create_files_list(self, generators: Iterable[Generator], root_folder):
        """
            create a table to show files in different folders
        """

        # create folder watcher using root_folder
        model = DiskFilesModel(generators, ("Name", "File Path", "Type", "Size"))

        filter_proxy_model = SortFilterModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(-1)

        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.table.verticalHeader().setVisible(0)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.sortByColumn(1, Qt.AscendingOrder)
        self.table.setModel(filter_proxy_model)
        self.table.setSortingEnabled(1)
        self.table.setShowGrid(0)
        self.table.setAlternatingRowColors(1)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.drives_tab.addTab(self.table, root_folder[:2])
        # self.drives_tab.adjustSize()

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
        self.msg_label = QLabel()
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
        self.setObjectName("shareManager")

        tick_icon = QIcon("data\\tick.png")
        arrow_icon = QIcon("data\\arrow.png")
        loading_icon = QIcon("data\\load.png")
        error_icon = QIcon("data\\error.png")
        back_icon = QIcon("data\\back.png")
        refresh_icon = QIcon("data\\refresh.png")

        self.icons = {0: arrow_icon, 1: tick_icon, 2: loading_icon, 3: error_icon}

        self.main_layout = QVBoxLayout()
        # use v layout for this widget
        self.setLayout(self.main_layout)
        self.files_present = QLabel("0 items")
        self.back_folder = QPushButton()
        self.back_folder.setIcon(back_icon)
        self.show_current_folder = QLineEdit("Home:\\")
        self.show_current_folder.setReadOnly(1)
        self.refresh_shared_files = QPushButton()
        self.refresh_shared_files.setObjectName("refreshBtn")
        self.refresh_shared_files.setIcon(refresh_icon)
        self.online_status_label = QLabel("Connect as:")
        self.online_users_dropdown = QComboBox()
        self.online_users_dropdown.setPlaceholderText("Select")
        self.online_users_dropdown.setToolTip("Select user to connect to")
        self.on_banner = 0

    def create_share_win(self):
        """
        create the window for share files tab
        """

        asfaUtils.close_window(self.main_layout)
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.online_status_label)
        hlayout.addWidget(self.online_users_dropdown)
        hlayout.addWidget(self.back_folder)
        hlayout.addWidget(self.show_current_folder)
        hlayout.addWidget(self.refresh_shared_files)
        # nest the inner hlayout
        self.main_layout.addLayout(hlayout)

        # create table for files display
        self.share_table = QTableView()
        # set a model before hand to avoid errors if self.add_files is not called right away
        self.share_table.setModel(QStandardItemModel())
        self.share_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.share_table.verticalHeader().setVisible(0)
        self.share_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.share_table.setSortingEnabled(1)
        self.share_table.setShowGrid(0)
        # self.share_table.setAlternatingRowColors(1)
        self.share_table.setEditTriggers(self.share_table.NoEditTriggers)
        self.main_layout.addWidget(self.share_table)
        self.main_layout.addWidget(self.files_present)
        self.on_banner = 0

    def add_files(self, generator: Generator):
        """
        create a table to show shared generator
        """

        self.share_model = ShareFilesModel(generator, ("Name", "Status", "Type", "Size"), self.icons)
        # set the model feedback to inner status bar
        self.share_model.feedback.connect(self.files_present.setText)
        self.share_table.setModel(self.share_model)


class SettingsWindow(QWidget):
    """
    Settings window
    inherits:
        QWidget
    """

    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("settingsWindow")

        # argument
        self.saved_settings = settings
        self.server_settings_win = ServerSettingsWindow()

        # main layouts
        self.outer_layout = QVBoxLayout()

        self.client_settings_group = QGroupBox("Client settings")
        self.client_settings_group.setObjectName("clientGroup")
        self.server_settings_group = QGroupBox("Server settings")
        self.server_settings_group.setObjectName("serverGroup")

        self.server_settings_layout = QVBoxLayout()
        self.server_settings_layout.addWidget(self.server_settings_win)
        # bind the server_settings_layout to groupbox
        self.server_settings_group.setLayout(self.server_settings_layout)

        # add the groups to the outer-most layout
        self.outer_layout.addWidget(self.client_settings_group)
        self.outer_layout.addWidget(self.server_settings_group)
        # bind the outer layout to the main window
        self.setLayout(self.outer_layout)

    def create_settings_widgets(self):
        """
        create the widgets for settings tab
        """

        # form layout for client settings
        form_layout = QFormLayout()
        # create fields
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Your Username")
        self.username_input.setText(self.saved_settings.choices["username"])

        self.download_location_input = PathEdit("Choose a folder to download to")
        self.download_location_input.setPlaceholderText("Select downloads folder")
        self.download_location_input.setText(self.saved_settings.choices["download_dir"])

        self.server_addr = QLineEdit()
        self.server_addr.setPlaceholderText("Server IP (Get this from your peer)")

        self.server_password_input = PasswordEdit()
        self.server_password_input.setPlaceholderText("Server password (Get this from your peer)")
        self.server_password_input.setText(self.saved_settings.choices["password"])

        self.apply_settings_btn = QPushButton("Apply changes")
        self.apply_settings_btn.setFixedSize(160, 35)
        self.apply_settings_btn.setObjectName("applyBtn")
        # set widgets to layout
        form_layout.addRow("Username", self.username_input)
        form_layout.addRow("Server IP", self.server_addr)
        form_layout.addRow("Password", self.server_password_input)
        form_layout.addRow("Download location", self.download_location_input)
        form_layout.addRow(self.apply_settings_btn)
        # set client group's layout
        self.client_settings_group.setLayout(form_layout)


# ------------------------------------- MAIN WINDOW -----------------------------------------
class MainWindow(QWidget):
    """
    main app window
    """

    center_statusbar_signal = pyqtSignal(str)
    right_statusbar_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("mainWindow")
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
        # saved settings
        self.saved_settings = Settings()
        self.saved_settings.load()

        self.vlayout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        # set the main window layout
        self.setLayout(self.vlayout)
        # add widgets to the layout
        self.main_tab = QTabWidget()
        self.main_tab.setDocumentMode(1)
        # modify the font
        font = self.main_tab.font()
        font.setPointSize(12)
        self.main_tab.setFont(font)
        # create the window to hold widgets that will go in the first tab
        self.disk_man = DiskManager(self)
        # self.disk_man.create_banner("Insert USB Drive")
        self.main_tab.insertTab(0, self.disk_man, "External Storage")
        # create the first tab
        self.disk_man.create_disk_win()
        # for the second tab
        self.share_man = ShareManager(self)
        self.share_man.create_share_win()
        self.main_tab.addTab(self.share_man, "Share Files")

        # create settings window
        self.settings_man = SettingsWindow(self.saved_settings, self)
        self.settings_man.create_settings_widgets()
        self.main_tab.addTab(self.settings_man, "Settings")

        # prepare downloads window
        self.downloads_win = asfaDownloads.DownloadsWindow()

        # create the status bars
        self.left_statusbar = QLabel()
        self.center_statusbar = QLabel()
        self.right_statusbar = QLabel()
        # add to horizontal layout
        self.hlayout.addWidget(self.left_statusbar)
        self.hlayout.addWidget(self.center_statusbar)
        self.hlayout.addWidget(self.right_statusbar)
        self.hlayout.setSpacing(2)

        # bind status signals
        self.center_statusbar_signal.connect(self.center_statusbar.setText)
        self.right_statusbar_signal.connect(self.right_statusbar.setText)

        # add the tab widget to the layout
        self.vlayout.addWidget(self.main_tab)
        # nest the status bar layout in the vertical main layout
        self.vlayout.addLayout(self.hlayout)

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

        # self.show()
        self.main_tab.currentChanged.connect(self.main_tab_changed)
        self.available_disks = set()
        self.local_usernames = {}
        self.total_files_sent = 0
        self.total_incomplete_sent = 0
        # get values from the settings tab
        # if no value set, ask the user or use default
        self.username = self.settings_man.username_input.text() or asfaUtils.USERNAME
        self.password = self.settings_man.server_password_input.text()
        self.download_to_folder = self.settings_man.download_location_input.text() or os.path.expanduser(f"~{common.OS_SEP}Downloads")
        self.settings_man.download_location_input.setText(self.download_to_folder)
        # if username was empty, set the one from asfaUtils
        self.settings_man.username_input.setText(self.username)

        # system tray icon
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.app_icon)
        self.tray.setToolTip("asfa App\nShare files")
        self.tray.messageClicked.connect(self._show_transfers_win)

        self.tray_menu = TrayMenu(self)
        self.tray_menu.more.clicked.connect(self.show_main_window)
        self.tray.setContextMenu(self.tray_menu)
        self.tray.show()

        # Folder tansfer win
        self.folder_transfers_win = FolderTransferWin(self.tray, self.saved_settings)
        self.folder_transfers_win.setWindowIcon(self.app_icon)
        self.folder_transfers_win.ok_button.clicked.connect(self.folder_transfer)
        self.tray_menu.to_transfer_win.clicked.connect(self._show_transfers_win)

        # scan for available ports and return one
        self.port = asfaUtils.get_port()
        # server uses local machine's IP
        self.server = server.Server()
        # set open port
        self.server.set_port(self.port)
        # set server signals
        self.server.signals.success.connect(self.right_statusbar.setText)
        self.server.signals.error.connect(self.center_statusbar.setText)
        # set event callbacks
        self.server.ftp_handler.on_file_sent = self.on_file_sent
        self.server.ftp_handler.on_incomplete_file_sent = self.on_incomplete_file_sent
        self.server.start()

        self.server_browser = browser.ServerBrowser()
        # set server_browser signals
        self.server_browser.signals.success.connect(self.right_statusbar.setText)
        self.server_browser.signals.error.connect(self.center_statusbar.setText)
        # set download folder
        self.server_browser.dst_dir = self.download_to_folder

        # set KeyBoard shortcuts
        self.disk_man.copy_shortcut.activated.connect(self.copy)
        self.disk_man.cut_shortcut.activated.connect(self.cut)
        # set focus shortcut
        self.disk_man.on_search_shortcut.activated.connect(self.focus_search_input)

        # share/downloads
        self.share_man.back_folder.clicked.connect(self.back_to_folder)
        self.share_man.share_table.doubleClicked.connect(self.share_double_click)
        self.share_man.refresh_shared_files.clicked.connect(self.update_shared_files)
        self.downloads_win.workers.worker_started.connect(self._on_download_started)
        self.downloads_win.workers.all_done.connect(self._change_icon_downloads_tab)

        self.worker_manager = WorkerManager()
        self.worker_manager.setWindowIcon(self.app_icon)

        # start the usb listener thread
        self.usb_thread = asfaUtils.DeviceListener()
        self.usb_thread.signals.on_change.connect(self.on_disk_changes)
        self.usb_thread.signals.error.connect(self.disk_man.create_banner)
        self.usb_thread.start()

        self.key_routes = {Qt.Key_Enter: self.open_file, Qt.Key_Return: self.open_file, Qt.Key_Delete: self.delete_files}
        self.sharefiles_routes = {Qt.Key_Enter: self.share_open_file, Qt.Key_Return: self.share_open_file}

        # update_n_save(username, password, download_dir)
        # self.saved_settings.update_n_save(self.username, self.password, self.download_to_folder)
        self.settings_man.apply_settings_btn.clicked.connect(self.change_settings)
        # server settings signal; add saved users to server authorizer
        self.settings_man.server_settings_win.new_user_signal.connect(self.authorize_user)
        self.settings_man.server_settings_win.delete_user_signal.connect(self.unauthorize_user)
        # saved users
        self.settings_man.server_settings_win.load_users()

        # for external storage
        # self.set_path(os.path.expanduser("~\\Music"))
        self.on_startup(self.usb_thread.disks)
        # put local machine on dropdown menu
        self.share_man.online_users_dropdown.currentTextChanged.connect(self.connect_to_user)
        # show window
        self.show()
        self.main_tab.setCurrentIndex(2)

    # ----------------------------- define server handler callbacks ------------------------------
    def on_dis_connect(self):
        message = f"{self.total_files_sent} sent, {self.total_incomplete_sent} incomplete sent"
        self.right_statusbar_signal.emit(message)

    def on_file_sent(self, file):
        self.total_files_sent += 1
        self.on_dis_connect()

    def on_incomplete_file_sent(self, file):
        self.total_incomplete_sent += 1
        message = f"{self.total_files_sent} sent, {self.total_incomplete_sent} incomplete sent"
        self.right_statusbar_signal.emit(message)
    # ----------------------------- end defining server handler callbacks ------------------------

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
        # show stats per disk
        self.files_model.layoutChanged.connect(self.update_stats)
        self.selection_model = self.table_view.selectionModel()
        self.selection_model.selectionChanged.connect(self.get_properties)
        # on tab change
        self.update_stats()
        self.get_properties()

    def change_settings(self):
        """ apply client settings/local changes """
        username = self.settings_man.username_input.text()
        server_ip = self.settings_man.server_addr.text()
        password = self.settings_man.server_password_input.text()
        download_to_folder = self.settings_man.download_location_input.text()
        if all((username, server_ip, password, download_to_folder)):
            self.username, self.password, self.download_to_folder = username, password, download_to_folder
            self.remote_addr = server_ip
            self.server_browser.dst_dir = self.download_to_folder
            # save settings
            self.saved_settings.update_n_save(self.username, self.password, self.download_to_folder)
            self.update_new_user((self.username, self.remote_addr))

    def authorize_user(self, username, password, shared_dir):
        """ slot for signal from server settings """
        self.server.setUser(username, password, shared_dir)

    def unauthorize_user(self, username):
        """ unauthorize already set user """
        self.server.delete_user(username)

    @property
    def selected_rows(self) -> tuple:
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
        get len of all files
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
            return False

    @property
    def isShareTableFocused(self) -> bool:
        try:
            table = self.share_man.share_table
            return (table.underMouse() and table.hasFocus())
        except Exception:
            return False

    def refresh_files_list(self):
        """ on refresh """
        folders = asfaUtils.get_folders(f"{self.current_disk_name}{common.OS_SEP}")
        file_generators = [common.get_files(folder) for folder in folders]
        model = DiskFilesModel(file_generators, ("Name", "File Path", "Type", "Size"))

        filter_proxy_model = SortFilterModel()
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(-1)
        self.table_view.setModel(filter_proxy_model)
        self.table_view.sortByColumn(1, Qt.AscendingOrder)
        self.tab_changed()
        self.update_stats()

    def get_properties(self, selected=None, deselected=None):
        """
        get the total size of all the selected files
        """
        if self.main_tab.currentIndex() == 0:
            self.get_disk_properties()

        elif self.main_tab.currentIndex() == 1:
            self.get_share_properties()
        else:
            self.left_statusbar.setText("")

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
            self.left_statusbar.setText(f"{len(rows):,} selected, {readable(total_size)}")
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
            self.left_statusbar.setText(f"{len(rows):,} selected, {readable(total_size)}")
        else:
            self.left_statusbar.setText("")

    def update_stats(self):
        """
        update info about files on main window
        """

        self.disk_man.disk_stats_label.setText(f"Disk: {self.current_disk_name}, Files: {self.total_files}")

    def closeEvent(self, e):
        """
        minimize on close
        """

        # self.tray.show()

        self.hide()
        e.ignore()

    def show_main_window(self):
        """
        slot for 'more' button in tray
        """

        # self.tray.hide()
        # show window
        self.showMaximized()

    def _show_transfers_win(self):
        """ slot for `transfer folders` button in tray """
        # self.tray.hide()
        self.folder_transfers_win.show()

    def _hide_transfers_win(self):
        """ hide folder transfer win """
        # self.tray.show()
        self.folder_transfers_win.hide()

    def _show_downloads_tab(self):
        """ insert downloads tab """
        self.main_tab.insertTab(2, self.downloads_win, "Downloads")
        self.main_tab.setTabIcon(2, self.download_icon)

    def _goto_downloads_tab(self):
        """ switch to downloads """
        self.main_tab.insertTab(2, self.downloads_win, "Downloads")
        self.main_tab.setCurrentIndex(2)

    def _change_icon_downloads_tab(self):
        """ close tab of main_tab """
        self.main_tab.setTabIcon(2, self.done_icon)

    def _on_download_started(self):
        """ slot for download started signal """
        self._show_downloads_tab()
        self.right_statusbar_signal.emit(f"Downloading to: {self.download_to_folder}")

    def disk_context_menu(self, e):
        """
        external storage popup menu
        parameter e:
            contextMenu event
        assumes:
            self.tab_changed has been called
            self.table_view has been defined
        """
        context = QMenu(self)
        if self.isDiskTableFocused:

            # addAction(self, QIcon, str, PYQT_SLOT, shortcut: Union[QKeySequence, QKeySequence.StandardKey, str, int] = 0)
            context.addAction(self.open_icon, "Open", self.open_file)
            context.addSeparator()
            context.addAction(self.copy_icon, "Copy", self.copy, "Ctrl+C")
            context.addAction(self.cut_icon, "Cut", self.cut, "Ctrl+X")
            context.addSeparator()
            context.addAction(self.delete_icon, "Delete", self.delete_files)
            context.addSeparator()
        context.addAction("Transfer Folders", self._show_transfers_win)
        context.exec_(e.globalPos())

    def share_context_menu(self, e):
        """
        share files popup menu
        parameter e:
            contextMenu event
        assumes:
            self.share_man.share_table has been defined
        """
        context = QMenu(self)
        if self.isShareTableFocused:

            # Name, Status, Type, Size
            # addAction(self, QIcon, str, PYQT_SLOT, shortcut: Union[QKeySequence, QKeySequence.StandardKey, str, int] = 0)

            context.addAction(self.download_icon, "Download", self.download_clicked)
            context.addSeparator()
            context.addAction(self.open_icon, "Open", self.share_menu_open)
            context.addSeparator()
            context.addAction(self.delete_icon, "Delete", self.handle_share_delete)
            context.addAction("I don't want to see this", self.handle_share_hide)
            context.addSeparator()
        context.addAction("Go to Downloads", self._goto_downloads_tab)
        context.exec_(e.globalPos())

    def contextMenuEvent(self, e):
        """
        window popup menu
        assumes:
            self.main_tab has been defined
        """
        if self.main_tab.currentIndex() == 0:
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
            self.center_statusbar_signal.emit("")
            self.disk_man.create_banner("Insert USB Drive")

    def set_events(self):
        """
        call on first disk insert
        """

        # call tab_changed whenever current tab changes
        self.disk_man.drives_tab.currentChanged.connect(self.tab_changed)
        # set signal callbacks; search on text change
        self.disk_man.search_input.textChanged.connect(self.search)
        # refresh btn update signals
        self.disk_man.refresh_files_btn.clicked.connect(self.refresh_files_list)

    def set_path(self, path: str):
        """
        update current folders and setup model/view
        """
        if self.disk_man.on_banner:
            self.disk_man.create_disk_win()
            self.set_events()

        folders = asfaUtils.get_folders(path)
        file_generators = [common.get_files(folder) for folder in folders]
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
                asfaUtils.utils_logger.debug(f"USB inserted: '{disk}'")
                self.set_path(disk)
                # self.tray.showMessage(f"asfa has detected Disk {disk}", "Transfer files here", self.app_icon)
                if not self.isVisible():
                    self._show_transfers_win()
            elif ejected:
                disk = ejected.pop()
                asfaUtils.utils_logger.debug(f"USB ejected: '{disk}'")
                index = self.index_from_tabText(disk[:2])
                self.disk_man.close_files_list(index)
                self.center_statusbar_signal.emit("")
        else:
            asfaUtils.utils_logger.debug("No USB drives available")
            self.available_disks = set()
            self.disk_man.create_banner("Insert USB Drive")
            self.center_statusbar_signal.emit("")

    def on_search(self):
        """
        slot for search button
        """

        string = self.disk_man.search_input.text()
        self.search(string)

    def focus_search_input(self):
        """ focus search QLineEdit """
        try:
            index = self.main_tab.currentIndex()
            # if external storage tab is selected
            if index == 0:
                self.disk_man.search_input.setFocus()
        except Exception:
            pass

    def search(self, search_txt):
        """
        change the search button icon and set the filter txt
        callback for QLineEdit textChanged event
        """

        if self.main_tab.currentIndex() == 0:
            # search 2 characters and above
            if len(search_txt) > 1:
                self.files_model.setFilterFixedString(search_txt)
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
        self.files_model.setFilterFixedString("")

    def on_double_click(self, s: QModelIndex):
        """
        open a file on double-click
        """

        self._open_file(s)

    def _open_file(self, index: QModelIndex):
        """ open file at index by default app """
        path = self.path_from_row(index)
        try:
            if self.main_tab.currentIndex() == 0:
                asfaUtils.start_file(path)
                asfaUtils.utils_logger.debug("File opened")

        except Exception as e:
            asfaUtils.utils_logger.debug(f"Opening file: {str(e)}")
            self.center_statusbar_signal.emit(f"File not found: '{path}'")
            # remove row from model
            self.files_model.removeRows(set((path, )))

    def path_from_row(self, row: QModelIndex):
        """
        get data from the first and the second column of row
        join them and return full file path
        """

        row = row.row()
        dirname = self.files_model.data(self.files_model.index(row, 1))
        file = self.files_model.data(self.files_model.index(row, 0))
        return os.path.join(dirname, common._basename(file))

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

        if self.main_tab.currentIndex() == 0:
            selected = self.selected_rows
            if selected:
                confirmation = self.ask(f"Delete {len(selected)} selected file(s) permanently?\n\nNote: This cannot be undone!")
                # if confirmation is YES
                if confirmation == QMessageBox.Yes:
                    to_delete = set()
                    for index in selected:
                        path = self.path_from_row(index)
                        asfaUtils.utils_logger.debug(f"Deleting permanently: '{path}'")
                        asfaUtils.delete_file(path)
                        to_delete.add(path)
                    # remove all rows from model before changing layout
                    self.files_model.removeRows(to_delete)
                    self.selection_model.clearSelection()
            else:
                self.center_statusbar_signal.emit("No file selected!")

    def open_file(self):
        """
        open last-selected file
        """

        try:
            index = self.selected_rows[-1]
            self._open_file(index)
        except IndexError:
            self.center_statusbar_signal.emit("No file selected!")

    def _handle_transfer(self, dst, task="copy"):
        """ prepare transfer workers/objects and enqueue them to manager """
        selected = self.selected_rows[::-1]
        to_delete = set()
        for index in selected:
            src = self.path_from_row(index)
            try:
                transfer_worker = asfaUtils.Transfer(
                    src, dst,
                    os.path.getsize(src),
                    task=task
                )
                self.worker_manager.enqueue(transfer_worker)
                if task == "move":
                    to_delete.add(src)
            except FileNotFoundError:
                to_delete.add(src)
        self.files_model.removeRows(to_delete)

    def copy(self):
        """
        copy files
        """

        if (self.main_tab.currentIndex() == 0) and not self.disk_man.on_banner:
            try:
                # get the dst from dialog
                dst = get_directory(self, "Copy selected items to...")
                # if dir selected
                if dst:
                    self.worker_manager.transfer_to.setText(f"Copying to '{dst}'")
                    self._handle_transfer(dst)

            except AttributeError:
                self.center_statusbar_signal.emit("Insert USB Drive")

    def cut(self):
        """
        cut files
        """

        if (self.main_tab.currentIndex() == 0) and not self.disk_man.on_banner:
            try:
                # get the dst from dialog
                dst = get_directory(self, "Move selected items to...")
                # if dir selected
                if dst:
                    self.worker_manager.transfer_to.setText(f"Moving to '{dst}'")

                    self._handle_transfer(dst, task="move")

            except AttributeError:
                self.center_statusbar_signal.emit("Insert USB Drive")

    def folder_transfer(self):
        """ handles transfers initiated from quick transfer window """
        try:
            # source_folder, dest_folder, copy, recurse, save_selection, ignore_patterns
            choice = self.folder_transfers_win.get_selections()
            src, dst, copy, isRecursive, save_selection, ignore = choice[0], choice[1], choice[2], choice[3], choice[4], choice[5]
            if all((src, dst)):

                # hide folders window
                self.folder_transfers_win.hide()

                if save_selection:
                    print("Save True")
                    disk = f"{self.current_disk_name}{common.OS_SEP}"
                    self.saved_settings.remember_disk(disk, src, dst, copy, isRecursive, save_selection)

                if copy:
                    print("Copy True")
                    self.worker_manager.transfer_to.setText(f"Copying to '{dst}'")
                    self._move_folder(src, dst, recurse=isRecursive, ignore_patterns=ignore)
                else:  # move
                    print("Move True")
                    self.worker_manager.transfer_to.setText(f"Moving to '{dst}'")
                    self._move_folder(src, dst, task="move", recurse=isRecursive, ignore_patterns=ignore)

        except Exception as e:
            print("Error >>>", e)

    def _move_folder(self, src_folder, dst_folder, task="copy", recurse=True, ignore_patterns=None):
        """ copy folder recursively """
        try:
            dst_name = common._basename(src_folder) or "Removable Disk"
            dst = os.path.join(dst_folder, dst_name)

            if not os.path.exists(dst):
                os.mkdir(dst)

            sorted_items = asfaUtils.get_files_folders(src_folder)

            for item in sorted_items:

                try:
                    # skip all links
                    if os.path.islink(item):
                        continue
                    # if it's a file, file is not a sys file
                    if os.path.isfile(item) and (not common.isSysFile(item)):

                        ext = os.path.splitext(item)[-1] or "without extensions"
                        if (ext.lower() in ignore_patterns):
                            # skip file with patttern
                            continue
                        # else, schedule to transfer
                        transfer_worker = asfaUtils.Transfer(
                            item, dst,
                            os.path.getsize(item),
                            task=task,
                        )
                        self.worker_manager.enqueue(transfer_worker)
                    elif os.path.isdir(item) and recurse:
                        # recurse
                        self._move_folder(item, dst, task=task, recurse=recurse, ignore_patterns=ignore_patterns)

                except Exception as e:
                    print(e)
                    self.center_statusbar_signal.emit(f"Error: skipping {item}")
                    continue

        except PermissionError:
            self.inform("Permission to create and write folder denied!\n\nLet's try that again with a different destination folder")

    # ----------------------- Let's start sharing files ---------------------------------------

    def back_to_folder(self):
        """ go back a folder """
        try:
            if len(self.server_browser.browser_history) > 1:
                # keep home dir for refreshing
                self.server_browser.browser_history.pop()
            folder = self.server_browser.browser_history[-1]
            self.update_shared_files(path=folder, fore=0)
        except IndexError:
            pass

    def update_shared_files(self, path=None, fore=1):
        """
        FTPS: fetch files from the specified path
        if path is None, refresh the cwd
        """

        self.server_browser.updateDir(path, forward=fore)
        generator = self.server_browser.getFilesList()
        self.share_man.add_files(generator)
        open_dir = f"Home:/{'/'.join(self.server_browser.browser_history)}"
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

        model = self.share_man.share_model
        row_data = model.data(row, role=Qt.UserRole)
        return row_data

    def download_clicked(self):
        """
        1. get selected files
        2. loop passing each file to download worker
        """

        selected = self.share_selected
        cwdir = "/".join(self.server_browser.browser_history)
        if selected:
            # pass in all the details needed for a successful login
            localhost = (self.username, self.password, self.remote_addr, self.port)

            for index in selected:
                name, f_exists, file_type, size = self.share_from_row(index)
                filename = os.path.join(self.download_to_folder, common._basename(name))
                # skip files that exist
                if os.path.exists(filename):
                    if (os.path.getsize(filename) == size):
                        continue
                if file_type == "Folder":
                    continue
                # -> function to change file status hence its icon, 2 for loading
                self.share_man.share_model._change_icon(filename, 2)
                # worker instance `w`
                w = asfaDownloads.Worker(filename, cwdir, size, localhost)
                # -> 1 for success
                w.signals.finished.connect(self.on_download_success)
                # -> 3 for error
                w.signals.error.connect(self.on_download_error)
                # -> 0 for cancelled
                w.signals.cancelled.connect(lambda file: self.share_man.share_model._change_icon(file, 0))
                # enqueue to worker manager
                self.downloads_win.workers.enqueue(w)

    def on_download_success(self, file):
        """ slot for download success signal """
        self.share_man.share_model._change_icon(file, 1)
        self.right_statusbar_signal.emit(f"Downloaded: {file}")
        self.center_statusbar_signal.emit(f"")

    def on_download_error(self, file, error):
        """ slot for download failure signal """
        self.share_man.share_model._change_icon(file, 3)
        self.center_statusbar_signal.emit(f"Couldn't download: {error}")
        self.right_statusbar_signal.emit(f"")

    def share_double_click(self, index: QModelIndex):
        """ respond to share table double-click """
        self.handle_share_open(index)

    def share_open_file(self):
        """
        open file if downloaded else download
        slot for `enter` button
        """
        try:
            index = self.share_selected[-1]
            self.handle_share_open(index)
        except IndexError:
            pass

    def share_menu_open(self):
        """
        called by Menu Open
        """
        try:
            index = self.share_selected[-1]
            self.handle_share_open(index, exclusive=True)
        except IndexError:
            pass

    def handle_share_delete(self):
        """ delete selected if downloaded """
        selected = self.share_selected[::-1]
        if selected:
            confirmation = self.ask(f"This is going to delete only the downloaded files.\n\nNote: This cannot be undone! Proceed?")
            # if confirmation is YES
            if confirmation == QMessageBox.Yes:
                for index in selected:
                    filename, f_exists, file_type, size = self.share_from_row(index)
                    path = os.path.join(self.download_to_folder, common._basename(filename))
                    if f_exists and (os.path.getsize(path) == size) and (file_type == "File"):
                        asfaUtils.delete_file(path)
                        asfaUtils.utils_logger.debug(f"Downloaded deleted: {path}")
                        # not downloaded, 0
                        self.share_man.share_model._change_icon(filename, 0)

    def handle_share_hide(self):
        """ remove row from model until next refresh """
        selected = self.share_selected
        row = self.share_from_row
        try:
            self.share_man.share_model.removeRows(set([row(index)[0] for index in selected]))
        except AttributeError:
            pass

    def handle_share_open(self, index, exclusive=False):
        """ goto folder or open downloaded file """
        filename, f_exists, file_type, size = self.share_from_row(index)
        if file_type == "Folder":
            self.update_shared_files(path=filename)
        else:
            # open files that exist
            path = os.path.join(self.download_to_folder, common._basename(filename))
            if os.path.exists(path) and (os.path.getsize(path) == size):
                asfaUtils.start_file(path)
            elif not exclusive:
                self.download_clicked()

    def update_new_user(self, user: tuple):
        """
        receive new users and add their details to dropdown menu
        """

        username, address = user
        if username not in self.local_usernames:
            # the IP address for the remote machine
            self.local_usernames[username] = address
            self.share_man.online_users_dropdown.clear()
            self.share_man.online_users_dropdown.addItems(self.local_usernames.keys())

    def connect_to_user(self, username):
        """ slot for recent dropdown currentTextChanged signal """
        addr = self.local_usernames.get(username)
        if addr:
            self.remote_addr = addr
            # the IP address for the remote machine, remote_addr
            self.server_browser.updateUser((username, self.password, self.remote_addr, self.port))
            # for share files tab
            self.update_shared_files()


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
    memory_usage = asfaUtils.psutil.Process(os.getpid()).memory_info().rss / 1048576
    print(f"[MEMORY USED] : {memory_usage} MB")

    sys.exit(app.exec_())
