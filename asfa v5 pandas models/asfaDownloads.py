__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


import sys
import os
from ftplib import FTP_TLS, error_perm
import common

from PyQt5.QtCore import (
    QAbstractListModel,
    QObject,
    QRect,
    QRunnable,
    Qt,
    QThreadPool,
    QTimer,
    pyqtSignal,
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

STATUS_WAITING = "waiting"
STATUS_RUNNING = "running"
STATUS_ERROR = "error"
STATUS_COMPLETE = "complete"
STATUS_STOPPED = "stopped"

STATUS_COLORS = {
    STATUS_RUNNING: "#33a02c",
    STATUS_ERROR: "#e31a1c",
    STATUS_STOPPED: "#cccccc",
    STATUS_COMPLETE: "#b2df8a",
}

DEFAULT_STATE = {"progress": 0, "status": STATUS_WAITING}


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        `str` unique job ID

    error
        `tuple` (exctype, value, traceback.format_exc() )

    progress
        `int` indicating % progress

    status
        `tuple` job ID, status string

    """
    __slots__ = ()

    error = pyqtSignal(str, str)

    finished = pyqtSignal(str)
    progress = pyqtSignal(str, int)
    status = pyqtSignal(str, str)


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

    def __init__(self, file: str, cwd: str, size: int):
        super().__init__()

        self.filename = common._basename(file)
        self.cwdir = cwd
        self.file_size = size
        down_size = self.file_size or 1024
        self.blocksize = min(down_size, 4194304)
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
            percentage = (self.transferred * 100) / self.file_size
            self.signals.progress.emit(self.job_id, percentage)
            if self.is_killed:
                self.ftp.abort()
                self.cleanup()
                # delete the partial file
                os.unlink(self.job_id)
                self.signals.status.emit(self.job_id, STATUS_STOPPED)
                return
        except Exception:
            pass

    @pyqtSlot()
    def run(self):
        """ start the file download """
        self.ftp = FTP_TLS()
        self.ftp.certfile = common.CERTF
        self.ftp.encoding = "utf-8"
        try:
            self.downloading_file = open(self.job_id, "wb")
            # localize write function to reduce overhead
            self.file_write = self.downloading_file.write
            # connect to the remote machine
            self.ftp.connect(self.addr, self.port)
            self.ftp.login()
            # set up a secure data channel
            self.ftp.prot_p()
            # switch to the right folder
            self.ftp.cwd(self.cwdir)
            self.signals.status.emit(self.job_id, STATUS_RUNNING)

            self.ftp.retrbinary(f"RETR {self.filename}", self.callback, blocksize=self.blocksize)

        # errror when the file is not found
        except error_perm as e:
            if not self.is_killed:
                self.cleanup()
                os.unlink(self.job_id)
                # swallow the error and emit signals
                self.signals.error.emit(self.job_id, str(e))
                self.signals.status.emit(self.job_id, STATUS_ERROR)

        # write permission denied (PermissionError)
        except Exception as e:
            if not self.is_killed:
                self.cleanup()
                try:
                    os.unlink(self.job_id)
                except Exception:
                    pass
                self.signals.error.emit(self.job_id, str(e))
                self.signals.status.emit(self.job_id, STATUS_ERROR)

        else:
            self.signals.status.emit(self.job_id, STATUS_COMPLETE)
            self.cleanup()
            self.signals.finished.emit(self.job_id)

    def kill(self):
        self.is_killed = 1


class WorkerManager(QAbstractListModel):
    """
    Manager to handle our worker queues and state.
    Also functions as a Qt data model for a view
    displaying progress for each worker.

    """

    _workers = {}
    _state = {}

    status = pyqtSignal(str)
    all_done = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Create a threadpool for our workers.
        self.downloads_threadpool = QThreadPool()
        self.total_errors = 0
        # set to download only one file at a time
        self.downloads_threadpool.setMaxThreadCount(1)
        print("Can download only %d file(s) at a time" % self.downloads_threadpool.maxThreadCount())

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
        worker.signals.error.connect(self.receive_error)
        worker.signals.status.connect(self.receive_status)
        worker.signals.progress.connect(self.receive_progress)
        worker.signals.finished.connect(self.done)

        self.downloads_threadpool.start(worker)
        self._workers[worker.job_id] = worker
        # Set default status to waiting, 0 progress.
        self._state[worker.job_id] = DEFAULT_STATE.copy()

        self.layoutChanged.emit()

    def receive_status(self, job_id, status):
        self._state[job_id]["status"] = status
        self.layoutChanged.emit()

    def receive_progress(self, job_id, progress):
        self._state[job_id]["progress"] = progress
        self.layoutChanged.emit()

    def receive_error(self, job_id, message):
        # print(message)
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
                # close downloads tab
                self.all_done.emit()
            self.layoutChanged.emit()
        except KeyError:
            pass

    def cleanup(self):
        """
        Remove any complete/failed workers from worker_state.
        """
        for job_id, s in list(self._state.items()):
            if s["status"] in (STATUS_COMPLETE, STATUS_ERROR, STATUS_STOPPED):
                del self._state[job_id]
        self.total_errors = 0
        self.layoutChanged.emit()

    def kill(self, job_id):
        if job_id in self._workers:
            self._workers[job_id].kill()
            self.done(job_id)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:

            job_ids = list(self._state.keys())
            job_id = job_ids[index.row()]
            return job_id, self._state[job_id]

    def rowCount(self, index):
        return len(self._state)


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
            color = QColor("#b2df8a")
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

        self.workers = WorkerManager()
        main_layout = QVBoxLayout()
        btns_layout = QHBoxLayout()

        self.progress = QListView()
        self.progress.setModel(self.workers)
        delegate = ProgressBarDelegate()
        self.progress.setItemDelegate(delegate)

        main_layout.addWidget(self.progress)

        stop = QPushButton("Cancel")
        stop.pressed.connect(self.stop_worker)

        clear = QPushButton("Clear")
        clear.pressed.connect(self.workers.cleanup)

        status_bar = QLabel()
        self.workers.status.connect(status_bar.setText)

        btns_layout.addWidget(status_bar)
        btns_layout.addStretch()
        btns_layout.addWidget(stop)
        btns_layout.addWidget(clear)
        main_layout.addLayout(btns_layout)
        self.setLayout(main_layout)

    def stop_worker(self):
        selected = self.progress.selectedIndexes()
        for idx in selected:
            job_id, _ = self.workers.data(idx, Qt.DisplayRole)
            self.workers.kill(job_id)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = DownloadsWindow()
    window.show()
    app.exec_()
