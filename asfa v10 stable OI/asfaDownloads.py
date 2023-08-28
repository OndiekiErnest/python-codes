__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


import sys
import os
import common

from PyQt5.QtCore import (
    QAbstractListModel,
    QRect,
    QRunnable,
    Qt,
    QThreadPool,
    QTimer,
    pyqtSlot,
)
from PyQt5.QtGui import QBrush, QColor, QPen, QPainter
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QApplication,
    QListView,
    QLabel,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)


downloads_logger = common.logging.getLogger(__name__)
downloads_logger.debug(f"Initializing {__name__}")


STATUS_WAITING = "waiting"
STATUS_RUNNING = "running"
STATUS_ERROR = "error"
STATUS_COMPLETE = "complete"

STATUS_COLORS = {
    STATUS_RUNNING: "#1a8602",  # luminous green
    STATUS_ERROR: "#e31a1c",  # red
    STATUS_COMPLETE: "#282828",  # dark gray
    STATUS_WAITING: "#cccccc",  # light gray
}

DEFAULT_STATE = {"progress": 0, "status": STATUS_WAITING}
EXISTS_STATE = {"progress": 100, "status": STATUS_COMPLETE}


class WorkerSignals(common.QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        `str` unique job ID

    error
        `tuple` job ID, error str

    progress
        (`str`, `float`, `float`) indicating job_id, % progress, file_size

    status
        `tuple` job ID, status string

    """
    __slots__ = ()

    error = common.pyqtSignal(str, str)
    cancelled = common.pyqtSignal(str)

    finished = common.pyqtSignal(str)
    progress = common.pyqtSignal(str, float, float)
    status = common.pyqtSignal(str, str)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.

    :param file: str filename
    :param size: file size

    """

    __slots__ = (
        "signals", "job_id", "is_killed", "filename", "file_write",
        "file_size", "cwdir"
    )

    def __init__(self, file: str, cwd: str, size: int, host: tuple):
        super().__init__()

        self.username, self.password, self.addr, self.port = host
        self.filename = common._basename(file)
        self.cwdir = cwd
        self.file_size = size
        down_size = self.file_size or 1024
        # down_size or 800 kB
        self.blocksize = min(down_size, 819200)
        # self.addr, self.port = None, 3000
        self.is_killed = 0
        self.transferred = 0
        self.signals = WorkerSignals()

        # give this job a unique ID, which is its dst path
        self.job_id = file
        self.signals.status.emit(self.job_id, STATUS_WAITING)

    def cleanup(self):
        """ close connection and the open file """
        try:
            self.ftp.quit()
        except Exception:
            self.ftp.close()
        self.downloading_file.close()
        self.ftp = None
        self.downloading_file = None
        self.is_killed = 1

    def callback(self, data):

        try:
            self.file_write(data)
            # emit the current progress signal
            self.transferred += len(data)
            self.signals.progress.emit(self.job_id, self.transferred, self.file_size)
            if self.is_killed:
                self.ftp.abort()
                self.cleanup()
                # delete the partial file
                os.unlink(self.job_id)
                self.signals.status.emit(self.job_id, STATUS_COMPLETE)
                return
        except Exception:
            pass

    @pyqtSlot()
    def run(self):
        """ start file download """
        self.ftp = common.ftp_tls()
        try:
            self.downloading_file = open(self.job_id, "wb")
            # localize write function to reduce overhead
            self.file_write = self.downloading_file.write
            # connect to the remote machine
            self.ftp.connect(self.addr, self.port)
            self.ftp.login(user=self.username, passwd=self.password)
            # set up a secure data channel
            self.ftp.prot_p()
            # switch to the right folder
            self.ftp.cwd(self.cwdir)
            self.signals.status.emit(self.job_id, STATUS_RUNNING)

            self.ftp.retrbinary(f"RETR {self.filename}", self.callback, blocksize=self.blocksize)

        # errror when the file is not found
        except common.error_perm as e:
            if not self.is_killed:
                self.cleanup()
                os.unlink(self.job_id)
                # swallow the error and emit signals
                downloads_logger.error(f"Couldn't download: {str(e)}")
                self.signals.error.emit(self.job_id, str(e))
                self.signals.status.emit(self.job_id, STATUS_ERROR)

        # write permission denied (PermissionError)
        except Exception as e:
            if not self.is_killed:
                error_msg = str(e)
                self.cleanup()
                try:
                    os.unlink(self.job_id)
                except Exception:
                    pass
                if e.errno == common.errno.WSAECONNREFUSED:
                    error_msg = "No connection could be made."
                downloads_logger.error(f"Couldn't download: {error_msg}")
                self.signals.error.emit(self.job_id, error_msg)
                self.signals.status.emit(self.job_id, STATUS_ERROR)

        else:
            downloads_logger.info(f"Downloaded: {self.job_id}")
            self.signals.status.emit(self.job_id, STATUS_COMPLETE)
            self.cleanup()
            self.signals.finished.emit(self.job_id)

    def kill(self):
        self.signals.cancelled.emit(self.job_id)
        self.is_killed = 1


class WorkerManager(QAbstractListModel):
    """
    Manager to handle our worker queues and state.
    Also functions as a Qt data model for a view
    displaying progress for each worker.

    """

    _workers = {}
    _state = {}

    status = common.pyqtSignal(str)
    current_task_progress = common.pyqtSignal(str)
    worker_started = common.pyqtSignal()
    all_done = common.pyqtSignal()

    def __init__(self):
        super().__init__()

        # Create a threadpool for our workers.
        self.downloads_threadpool = QThreadPool()
        self.total_errors = 0
        # set files to download at a time
        self.downloads_threadpool.setMaxThreadCount(1)
        downloads_logger.debug(f"Can download {self.downloads_threadpool.maxThreadCount()} file(s) at a time")

        self.status_timer = QTimer()
        self.status_timer.setInterval(100)
        self.status_timer.timeout.connect(self.notify_status)
        self.status_timer.start()

    def notify_status(self):
        """ update the user of the remaining downloads """
        # running = min(n_workers, self.max_threads)
        # rem_downloads = max(1, len(self._workers) - self.max_threads)
        self.status.emit(f"{len(self._workers)} remaining, {self.total_errors} errors")

    def enqueue(self, worker):
        """
        Enqueue a worker to run (at some point) by passing it to the QThreadPool.
        """
        self.worker_started.emit()
        worker.signals.error.connect(self.receive_error)
        worker.signals.status.connect(self.receive_status)
        worker.signals.progress.connect(self.receive_progress)
        worker.signals.finished.connect(self.done)

        self._workers[worker.job_id] = worker
        # Set default status to waiting, 0 progress.
        self._state[worker.job_id] = DEFAULT_STATE.copy()

        self.downloads_threadpool.start(worker)
        self.layoutChanged.emit()

    def receive_status(self, job_id, status):
        try:
            self._state[job_id]["status"] = status
            self.layoutChanged.emit()
        except KeyError:
            pass

    def receive_progress(self, job_id, progress, file_size):
        try:
            percentage = (progress * 100) / file_size
            self._state[job_id]["progress"] = percentage
            self.current_task_progress.emit(f"{common.convert_bytes(progress)} / {common.convert_bytes(file_size)} | {job_id}")
            self.layoutChanged.emit()
        except KeyError:
            self.current_task_progress.emit("")

    def receive_error(self, job_id, message):
        downloads_logger.debug(f"Error downloading: {message}")
        self.total_errors += 1
        self.done(job_id)

    def done(self, job_id):
        """
        Task/worker complete. Remove it from the active workers
        dictionary. We leave it in worker_state, as this is used to
        to display past/complete workers too.
        """
        try:
            del self._workers[job_id]
            if not self._workers:
                # signal to close downloads tab
                self.all_done.emit()
            self.layoutChanged.emit()
            self.current_task_progress.emit("")
        except KeyError:
            pass

    def cleanup(self):
        """
        Remove any complete/failed workers from worker_state.
        """
        for job_id, s in list(self._state.items()):
            if s["status"] in (STATUS_COMPLETE, STATUS_ERROR):
                del self._state[job_id]
        self.total_errors = 0
        self.layoutChanged.emit()

    def kill(self, job_id):
        if job_id in self._workers:
            self._workers[job_id].kill()
            del self._state[job_id]
            # delete job_id and emit layout change
            self.done(job_id)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:

            job_ids = list(self._state.keys())
            job_id = job_ids[index.row()]
            return job_id, self._state[job_id]

    def rowCount(self, index):
        return len(self._state)

    def add_row(self, name: str):
        """ add row to model if name is of a file that exists """
        self._state[name] = EXISTS_STATE.copy()


class ProgressBarDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index):
        # data is our status dict, containing progress, id, status
        job_id, data = index.model().data(index, Qt.DisplayRole)
        if data["progress"] > 0:
            color = QColor(STATUS_COLORS[data["status"]])

            brush = QBrush()
            brush.setColor(color)
            brush.setStyle(Qt.SolidPattern)

            width = option.rect.width() * data["progress"] / 100

            #  Copy of the rect, so we can modify.
            rect = QRect(option.rect)
            rect.setWidth(width)

        else:
            color = QColor(STATUS_COLORS[data["status"]])
            brush = QBrush()
            brush.setColor(color)
            brush.setStyle(Qt.SolidPattern)
            rect = option.rect

        if option.state & QStyle.State_Selected:
            brush = QBrush()
            brush.setColor(QColor("#03afff"))
            brush.setStyle(Qt.SolidPattern)

        pen = QPen()
        pen.setColor(Qt.black)
        painter.fillRect(rect, brush)
        painter.drawText(option.rect, Qt.AlignLeft, job_id)


class DownloadsWindow(QWidget):
    """
    window for displaying downloading files
    inherits:
        QWidget
    """

    def __init__(self):
        super().__init__()

        self.setObjectName("downloadsWin")
        self.workers = WorkerManager()
        self.download_location = ""
        main_layout = QVBoxLayout()
        btns_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        main_layout.addLayout(btns_layout)

        self.d_location_label = QLabel()
        self.d_location_label.setAlignment(Qt.AlignRight)

        self.progress_view = QListView()
        self.progress_view.setAlternatingRowColors(True)
        self.progress_view.clicked.connect(self.change_cancel_btn)
        self.progress_view.setModel(self.workers)
        delegate = ProgressBarDelegate()
        self.progress_view.setItemDelegate(delegate)

        main_layout.addWidget(self.progress_view)

        self.stop = QPushButton("Cancel")
        self.stop.setToolTip("Stop downloading selected files")
        self.stop.setDisabled(True)
        self.stop.clicked.connect(self.stop_worker)

        clear = QPushButton("Clear")
        clear.setToolTip("Temporarily clear the files list from view")
        clear.pressed.connect(self.workers.cleanup)

        self.now_downloading = QLabel()

        status_bar = QLabel()
        self.workers.status.connect(status_bar.setText)
        self.workers.current_task_progress.connect(self.now_downloading.setText)

        btns_layout.addWidget(self.stop)
        btns_layout.addWidget(clear)
        btns_layout.addWidget(self.now_downloading)
        btns_layout.addStretch()

        bottom_layout.addWidget(status_bar)
        bottom_layout.addWidget(self.d_location_label)

        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def change_cancel_btn(self):
        """ enable cancel btn when item clicked """
        selected = self.progress_view.selectedIndexes()
        if selected:
            _, status = self.workers.data(selected[0])
            if status.get("status") == "running":
                self.stop.setEnabled(True)
            else:
                self.stop.setDisabled(True)

    def stop_worker(self):
        selected = self.progress_view.selectedIndexes()
        if selected:
            for idx in selected:
                job_id, _ = self.workers.data(idx)
                self.workers.kill(job_id)
                downloads_logger.debug(f"Downloading cancelled: '{job_id}'")
            self.stop.setDisabled(True)

    def change_title(self, text: str):
        """ change title info """
        if text:
            self.download_location = text
            self.d_location_label.setText(f"Download location: '{self.download_location}'")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = DownloadsWindow()
    window.show()
    app.exec_()
