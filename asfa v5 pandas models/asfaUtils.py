__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


import uuid
import time
from typing import Generator, List
import os
import socket
import logging
import psutil
from PyQt5.QtCore import QRunnable, QThread, QObject, pyqtSignal, pyqtSlot
import common

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


USERNAME = socket.getfqdn()


def isPortAvailable(port) -> bool:
    """
    test and see if a port number is open
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", port))
    return not (result == 0)


def get_port() -> int:
    """ get available port """
    for i in range(3000, 4067):
        if isPortAvailable(i):
            return i


class DeviceSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    error
    `str` Exception string
    on_change
    `list` data returned from processing
    """
    __slots__ = ()
    error = pyqtSignal(str)
    on_change = pyqtSignal(list)


class DeviceListener(QThread):
    """
    trigger a callback when a device has been plugged in or out
    """
    __slots__ = ("signals", "disks", "is_running", "change")

    def __init__(self):
        super().__init__()
        self.setTerminationEnabled(1)
        self.signals = DeviceSignals()
        # check on startup
        self.disks = self.list_drives()
        self.is_running = 0
        self.change = len(self.disks)

    @pyqtSlot()
    def run(self):
        self.is_running = 1
        while self.is_running:
            self.disks = self.list_drives()
            available = len(self.disks)
            if self.change != available:
                self._on_change(self.disks)
                self.change = available
            time.sleep(0.9)

    def list_drives(self) -> List[str]:
        """
        Get a list of drives using psutil
        :return: list of drives
        """

        try:
            return [i.mountpoint for i in psutil.disk_partitions() if "removable" in i.opts]
        except TypeError:
            self.signals.error.emit("Failed to enumerate drives")
            return []

    def _on_change(self, drives: List):
        """ emit signal of new disks """
        self.signals.on_change.emit(self.disks)

    def close(self):

        self.is_running = 0


class TransferSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
    `str` transfer id
    progress
    `int` indicating % progress
    """
    __slots__ = ()
    finished = pyqtSignal(str)
    progress = pyqtSignal(str, int)
    transferred = pyqtSignal(str, float)


class Transfer(QRunnable):
    """
    File transfer runnable
    Runs on a different thread
    inherits:
        QRunnable
    parameters:
        `src`: str file path
        `dst`: str file/dir path
        `size`: float `src` file size in bytes
        `model`: QStandardModel files model
        `indx`: QModelIndex `model` index for `src`
    """
    __slots__ = (
        "src", "dst", "size", "model", "task",
        "index", "signals", "running", "job_id")

    def __init__(self, src, dst, size, task="copy"):
        super().__init__()
        self.setAutoDelete(1)
        self.src = src
        self.dst = dst
        self.size = size
        self.task = task
        self.signals = TransferSignals()
        self.running = 0
        # Give this job a unique ID.
        self.job_id = str(uuid.uuid4())

    @pyqtSlot()
    def run(self):
        # model and index are passed on move files
        if self.task == "copy":
            self.copy(self.src, self.dst)
        elif self.task == "move":
            self.move(self.src, self.dst)

    def _copyfileobj_readinto(self, fsrc, fdst, length=1048576):
        """
        readinto()/memoryview()-based variant of copyfileobj()
        *fsrc* must support readinto() method and both files must be
        open in binary mode.
        """
        progress = 0
        self.running = 1
        # localize variable access to minimize overhead
        fsrc_readinto = fsrc.readinto
        fdst_write = fdst.write
        with memoryview(bytearray(length)) as mv:
            try:
                while 1:
                    n = fsrc_readinto(mv)
                    if not n:
                        self.signals.finished.emit(self.job_id)
                        self.running = 0
                        return 1

                    elif n < length:
                        with mv[:n] as smv:
                            fdst.write(smv)
                    else:
                        fdst_write(mv)
                    progress += n
                    percentage = (progress * 100) / self.size
                    self.signals.transferred.emit(self.job_id, progress)
                    self.signals.progress.emit(self.job_id, percentage)
                    # handle cancel
                    if not self.running:
                        self.signals.progress.emit(self.job_id, 100)
                        self.signals.finished.emit(self.job_id)
                        return 0
            except FileNotFoundError:
                self.running = 0
                self.signals.progress.emit(self.job_id, 100)
                self.signals.finished.emit(self.job_id)
                return 0

    def _copyfileobj(self, fsrc, fdst, length=1048576):
        """
        copy data from file-like object fsrc to file-like object fdst
        return 1 on success, 0 otherwise
        """
        progress = 0
        self.running = 1
        # localize variables to avoid overhead
        fsrc_read = fsrc.read
        fdst_write = fdst.write
        try:
            while 1:
                buff = fsrc_read(length)
                if not buff:
                    self.signals.finished.emit(self.job_id)
                    self.running = 0
                    # break and return success
                    return 1
                fdst_write(buff)
                progress += len(buff)
                percentage = (progress * 100) / self.size
                self.signals.transferred.emit(self.job_id, progress)
                self.signals.progress.emit(self.job_id, percentage)
                # handle cancel
                if not self.running:
                    self.signals.progress.emit(self.job_id, 100)
                    self.signals.finished.emit(self.job_id)
                    return 0

        except FileNotFoundError:
            self.running = 0
            self.signals.progress.emit(self.job_id, 100)
            self.signals.finished.emit(self.job_id)
            return 0

    def _copyfile(self, src, dst):
        if file_exists(src, dst):
            # end prematurely and return success, 1
            self.signals.progress.emit(self.job_id, 100)
            self.signals.finished.emit(self.job_id)
            return 1
        else:
            with open(src, 'rb') as fsrc:
                with open(dst, 'wb') as fdst:
                    if self.size > 0:
                        return self._copyfileobj_readinto(fsrc, fdst, length=min(1048576, self.size))
                    # copy files with 0 sizes
                    return self._copyfileobj(fsrc, fdst)

    def copy(self, src, dst):
        if os.path.isdir(dst):
            dst = os.path.join(dst, common._basename(src))
            self.dst = dst
        done = self._copyfile(src, dst)
        if not done:
            # clean up incomplete dst file
            delete_file(dst)
        return done

    def move(self, src, dst):
        done = self.copy(src, dst)
        if done:
            # delete source file only on success
            delete_file(src)


class Thread(QThread):
    """
    run `func` in QThread
    """
    __slots__ = ("func", "args")
    results = pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.setTerminationEnabled(1)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        try:
            finished = self.func(*self.args, **self.kwargs)
            self.results.emit(finished)
        except Exception as e:
            print("[Error running function in thread]", e)


class ThreadBase(QThread):
    """
    Abstract implementation for `BroadcastUser` and `ReceiveUser`
    """
    __slots__ = ("is_running")

    def __init__(self):
        super().__init__()
        self.setTerminationEnabled(1)
        self.is_running = 0

    @pyqtSlot()
    def run(self):
        self.is_running = 1
        self.task()

    def task(self):
        pass

    def close(self):
        """ set running flag to 0 """
        self.is_running = 0


class BroadcastUser(ThreadBase):
    """
    Broadcast username
    """
    __slots__ = ()

    def task(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # this is a broadcast socket
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("", common.BR_PORT))

        while self.is_running:
            data = f"{common.BR_SIGN}{USERNAME}"
            s.sendto(data.encode(), ("<broadcast>", common.BR_PORT))
            time.sleep(3)


class ReceiveUser(ThreadBase):
    """
    Receive username
    """
    __slots__ = ()
    new_user = pyqtSignal(tuple)

    def task(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(4)
        # this is a broadcast socket
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("", common.BR_PORT + 3))
        while self.is_running:
            data, addr = s.recvfrom(1024)
            data = data.decode()
            if data.startswith(common.BR_SIGN):
                name = data[len(common.BR_SIGN):]
                self.new_user.emit((name, addr[0]))


def close_window(layout):
    """
    delete PyQt5 widgets recursively
    assumes:
        layout is a valid QLayout class
    """

    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                close_window(child.layout())


def start_file(filename):
    """
    open file using the default app
    """
    try:
        os.startfile(filename)
    except Exception:
        pass


def file_exists(src, dst):
    """ compare file properties """
    if os.path.isdir(dst):
        dst = os.path.join(dst, common._basename(src))
    if os.path.exists(dst):
        return (os.path.getsize(src) == os.path.getsize(dst))
    return False


def delete_file(filename):
    """
    permanently delete a file
    """
    try:
        os.unlink(filename)
    except FileNotFoundError:
        pass


def trim_text(txt: str, length: int) -> str:
    """
    reduce the length of a string to the specified length
    """
    if len(txt) > length:
        return f"{txt[:length]}..."
    else:
        return txt


def get_folder_extensions(folder):
    """ scan dir and yield extensions in folder, and file size"""
    for entry in os.scandir(folder):
        try:
            full_path = entry.path
            # avoid listing folder-info files
            if entry.is_file() and not common.isSysFile(full_path):
                size = os.path.getsize(full_path)
                ext = os.path.splitext(full_path)[-1] or "without extensions"
                yield (ext.lower(), size)
        except Exception:
            continue


def get_ext_recursive(folder):
    """ walk through folders and yield unique extensions """
    extensions = set()
    total_size = 0
    for subfolders in get_folders(folder):
        for ext, size in get_folder_extensions(subfolders):
            extensions.add(ext)
            total_size += size
    exts_lst = list(extensions)
    exts_lst.sort()
    return (total_size, exts_lst)


def get_folders(path: str) -> List[str]:
    """
    return all recursive folders in path
    return empty folder if path doesn't exist
    """

    folders = []
    if os.path.exists(path):
        for folder, subfolders, files in os.walk(path):
            if files:
                folders.append(folder)
        # folders.sort()
    return folders


def get_files_folders(path: str):
    """ return a sorted list of files first and lastly folders """
    items = []
    for entry in os.scandir(path):
        if entry.is_file():
            # put files at the beginning
            items.insert(0, entry.path)
        else:
            # put folders at the end
            items.append(entry.path)
    return items
