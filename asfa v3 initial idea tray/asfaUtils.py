__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"

import uuid
import time
from typing import Generator, List
import os
import socket
import mimetypes
import win32api
import win32con
import win32gui
import logging
import psutil
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
mimetypes.init()


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


class DeviceListener(QRunnable):
    """
    Listens to Win32 `WM_DEVICECHANGE` messages
    and trigger a callback when a device has been plugged in or out

    See: https://docs.microsoft.com/en-us/windows/win32/devio/wm-devicechange
    """
    __slots__ = ("signals", "disks", "hwnd")
    WM_DEVICECHANGE_EVENTS = {
        0x0019: ('DBT_CONFIGCHANGECANCELED', 'A request to change the current configuration (dock or undock) has been canceled.'),
        0x0018: ('DBT_CONFIGCHANGED', 'The current configuration has changed, due to a dock or undock.'),
        0x8006: ('DBT_CUSTOMEVENT', 'A custom event has occurred.'),
        0x8000: ('DBT_DEVICEARRIVAL', 'A device or piece of media has been inserted and is now available.'),
        0x8001: ('DBT_DEVICEQUERYREMOVE', 'Permission is requested to remove a device or piece of media. Any application can deny this request and cancel the removal.'),
        0x8002: ('DBT_DEVICEQUERYREMOVEFAILED', 'A request to remove a device or piece of media has been canceled.'),
        0x8004: ('DBT_DEVICEREMOVECOMPLETE', 'A device or piece of media has been removed.'),
        0x8003: ('DBT_DEVICEREMOVEPENDING', 'A device or piece of media is about to be removed. Cannot be denied.'),
        0x8005: ('DBT_DEVICETYPESPECIFIC', 'A device-specific event has occurred.'),
        0x0007: ('DBT_DEVNODES_CHANGED', 'A device has been added to or removed from the system.'),
        0x0017: ('DBT_QUERYCHANGECONFIG', 'Permission is requested to change the current configuration (dock or undock).'),
        0xFFFF: ('DBT_USERDEFINED', 'The meaning of this message is user-defined.'),
    }

    def __init__(self):
        super().__init__()
        self.setAutoDelete(1)
        self.signals = DeviceSignals()
        # check on startup
        self.disks = self.list_drives()

    def _create_window(self):
        """
        Create a window for listening to messages
        https://docs.microsoft.com/en-us/windows/win32/learnwin32/creating-a-window#creating-the-window

        See also: https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-createwindoww

        :return: window hwnd
        """
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._on_message
        wc.lpszClassName = self.__class__.__name__
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        return win32gui.CreateWindow(class_atom, self.__class__.__name__, 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)

    @pyqtSlot()
    def run(self):
        logger.info(f'Listening to drive changes')
        self.hwnd = self._create_window()
        logger.debug(f'Created listener window with hwnd={self.hwnd:x}')
        logger.debug(f'Listening to messages')
        win32gui.PumpMessages()

    def _on_message(self, hwnd: int, msg: int, wparam: int, lparam: int):
        if msg != win32con.WM_DEVICECHANGE:
            return 0
        event, description = self.WM_DEVICECHANGE_EVENTS[wparam]
        logger.debug(f'Received message: {event} = {description}')
        if event in ('DBT_DEVICEREMOVECOMPLETE', 'DBT_DEVICEARRIVAL'):
            self._on_change(self.list_drives())
        return 0

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

        self.disks = drives
        self.signals.on_change.emit(self.disks)

    def close(self):

        win32gui.PostMessage(self.hwnd, win32con.WM_QUIT, 0, 0)


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
    etime = pyqtSignal(str, int)
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
        "src", "dst", "size", "model",
        "index", "signals", "running", "job_id")

    def __init__(self, src, dst, size, model=None, indx=None):
        super().__init__()
        self.setAutoDelete(1)
        self.src = src
        self.dst = dst
        self.size = size
        self.model = model
        self.index = indx
        self.signals = TransferSignals()
        self.running = 0
        # Give this job a unique ID.
        self.job_id = str(uuid.uuid4())

    @pyqtSlot()
    def run(self):
        # model and index are passed on move files
        if self.model is None:
            self.copy(self.src, self.dst)
        else:
            self.move(self.src, self.dst)

    def _copyfileobj(self, fsrc, fdst, length=1048576):
        """copy data from file-like object fsrc to file-like object fdst
        return 1 on success, 0 otherwise
        """
        progress = 0
        self.running = 1
        starttime = time.time()
        try:
            while 1:
                buff = fsrc.read(length)
                if not buff:
                    self.signals.finished.emit(self.job_id)
                    self.running = 0
                    # break and return success
                    return 1
                fdst.write(buff)
                progress += len(buff)
                percentage = (progress * 100) / self.size
                time_diff = time.time() - starttime
                progress_diff = 100 - percentage
                # estimate time remaining
                rem_time = (time_diff * progress_diff) / percentage
                self.signals.etime.emit(self.job_id, int(rem_time))
                self.signals.transferred.emit(self.job_id, progress)
                self.signals.progress.emit(self.job_id, percentage)
                # handle cancel
                if not self.running:
                    self.signals.progress.emit(self.job_id, 100)
                    self.signals.finished.emit(self.job_id)
                    return 0
        except Exception:
            self.signals.progress.emit(self.job_id, 100)
            self.signals.finished.emit(self.job_id)
            return 0

    def _samefile(self, src, dst):
        if os.path.exists(dst):
            # use file stats to compare more fields
            src_stats = os.stat(src)
            dst_stats = os.stat(dst)
            return (src_stats.st_size == dst_stats.st_size)
        else:
            return False

    def _copyfile(self, src, dst):
        if file_exists(src, dst):
            # end prematurely and return success, 1
            self.signals.etime.emit(self.job_id, 0)
            self.signals.progress.emit(self.job_id, 100)
            self.signals.finished.emit(self.job_id)
            return 1
        else:
            with open(src, 'rb') as fsrc:
                with open(dst, 'wb') as fdst:
                    return self._copyfileobj(fsrc, fdst)

    def copy(self, src, dst):
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))
            self.dst = dst
        done = self._copyfile(src, dst)
        if not done:
            # clean up dst file on cancel failure
            delete_file(dst)
        return done

    def move(self, src, dst):
        done = self.copy(src, dst)
        if done:
            # delete and remove file from model only on success
            delete_file(src)
            self.model.removeRow(self.index.row())


def close_window(layout):
    """
    delete PyQt5 widgets recursively
    assumes:
        layout is not empty
    """

    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                close_window(child.layout())


def file_category(filename: str):
    """ guess file mime type """
    mimestart = mimetypes.guess_type(filename)[0]
    if mimestart is not None:
        return mimestart.split("/")[0]
    else:
        return "application"


def start_file(filename):
    """
    open file using the default app
    """
    try:
        os.startfile(filename)
    except Exception as e:
        print("[Error Opening File]", e)


def file_exists(src, dst):
    """ compare file properties """
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if os.path.exists(dst):
        return (os.path.getsize(src) == os.path.getsize(dst))
    else:
        return False


def isPortAvailable(port) -> bool:
    """
    test and see if a port number is free
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    return not (result == 0)


def delete_file(filename):
    """
    permanently delete a file
    """
    try:
        os.unlink(filename)
    except Exception:
        pass


def convert_bytes(num: int) -> str:
    """ format bytes to respective units for presentation (max GB)"""
    if num >= 1073741824:
        return f"{round(num / 1073741824, 2)} GB"
    elif num >= 1048576:
        return f"{round(num / 1048576, 2)} MB"
    elif num >= 1024:
        return f"{round(num / 1024, 2)} KB"
    else:
        return f"{num} Bytes"


def trim_text(txt: str, length: int) -> str:
    """
    reduce the length of a string to the specified length
    """
    if len(txt) > length:
        return f"{txt[:length]}..."
    else:
        return txt


def get_files(folder: str) -> Generator:
    """
    return the file and its stats
    """

    file_excludes = {"AlbumArtSmall.jpg", "Folder.jpg", "desktop.ini"}
    other_file_excludes = ("AlbumArt_",)
    for entry in os.scandir(folder):
        # avoid listing folder-info files
        if entry.is_file() and not (entry.name.startswith(other_file_excludes) or entry.name in file_excludes):
            ext = os.path.splitext(entry.name)[-1]
            ext = f"{ext.strip('.').upper()} File"
            stats = entry.stat()
            size = convert_bytes(stats.st_size)
            yield entry.name, folder, ext, size


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
        folders.sort()
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
