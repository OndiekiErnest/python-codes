__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


import uuid
import time
import socket
import psutil
from PyQt5.QtCore import QRunnable, QThread, pyqtSlot
import common

utils_logger = common.logging.getLogger(__name__)

utils_logger.debug(f"Initializing {__name__}")


USERNAME = socket.getfqdn()


def isPortAvailable(port) -> bool:
    """
    test and see if a port number is open
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", port))
    return not (result == 0)


def isRemovable(path: str):
    try:
        return (path in {i.mountpoint for i in psutil.disk_partitions() if "removable" in i.opts})
    except Exception:
        return False


def get_port() -> int:
    """ get available port """
    for i in range(3000, 4067):
        if isPortAvailable(i):
            return i


class DeviceSignals(common.QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    error
    `str` Exception string
    on_change
    `list` data returned from processing
    """
    __slots__ = ()
    error = common.pyqtSignal(str)
    on_change = common.pyqtSignal(list)


class DeviceListener(QThread):
    """
    trigger a callback when a device has been plugged in or out
    """
    __slots__ = ("signals", "disks", "is_running", "change")

    def __init__(self):
        utils_logger.info("Starting USB drive listener")

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

    def list_drives(self) -> list:
        """
        Get a list of drives using psutil
        :return: list of drive str
        """

        try:
            return [i.mountpoint for i in psutil.disk_partitions() if "removable" in i.opts]
        except Exception as e:
            utils_logger.error(f"Error listing drives: {str(e)}")
            self.signals.error.emit("Failed to enumerate drives")
            return []

    def _on_change(self, drives: list):
        """ emit signal of new disks """
        self.signals.on_change.emit(self.disks)

    def close(self):
        utils_logger.debug("Closing USB drive listener")
        self.is_running = 0


class TransferSignals(common.QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
    `str` transfer id
    progress
    `int` indicating % progress
    """
    __slots__ = ()
    finished = common.pyqtSignal(str)
    progress = common.pyqtSignal(str, int)
    transferred = common.pyqtSignal(str, float)
    duplicate = common.pyqtSignal(str)


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
        # run the specified function
        if self.task == "copy":
            utils_logger.debug(f"Copying files to '{self.dst}'")
            self.copy(self.src, self.dst)
        elif self.task == "move":
            utils_logger.debug(f"Moving files to '{self.dst}'")
            self.move(self.src, self.dst)

    def _copyfileobj_readinto(self, fsrc, fdst, length=1048576):
        """
        readinto()/memoryview()-based variant of copyfileobj()
        *fsrc* must support readinto() method and both files must be
        open in binary mode.
        """
        utils_logger.debug(f"Transferring, method: readinto, buffer: {length}")
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
                        utils_logger.debug("Successful transfer")
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
                        utils_logger.debug("Cancelled transfer")
                        self.signals.progress.emit(self.job_id, 100)
                        self.signals.finished.emit(self.job_id)
                        return 0
            except Exception as e:
                utils_logger.error(f"Error in transferring: {str(e)}")
                self.running = 0
                self.signals.progress.emit(self.job_id, 100)
                self.signals.finished.emit(self.job_id)
                return 0

    def _copyfileobj(self, fsrc, fdst, length=1048576):
        """
        copy data from file-like object fsrc to file-like object fdst
        return 1 on success, 0 otherwise
        """
        utils_logger.debug(f"Transferring, method: copy-buffer, buffer: {length}")
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
                    utils_logger.debug("Successful transfer")
                    return 1
                fdst_write(buff)
                progress += len(buff)
                percentage = (progress * 100) / self.size
                self.signals.transferred.emit(self.job_id, progress)
                self.signals.progress.emit(self.job_id, percentage)
                # handle cancel
                if not self.running:
                    utils_logger.debug("Cancelled transfer")
                    self.signals.progress.emit(self.job_id, 100)
                    self.signals.finished.emit(self.job_id)
                    return 0

        except Exception as e:
            utils_logger.error(f"Error in transferring: {str(e)}")
            self.running = 0
            self.signals.progress.emit(self.job_id, 100)
            self.signals.finished.emit(self.job_id)
            return 0

    def _copyfile(self, src, dst):
        """ check if file exists, if same filesystem, else prepare file objects """
        if file_exists(src, dst):
            # end prematurely and return success, 1
            utils_logger.debug(f"File already exists '{dst}'")
            self.signals.duplicate.emit(dst)
            self.signals.progress.emit(self.job_id, 100)
            self.signals.finished.emit(self.job_id)
            return 1

        elif same_filesystem(src, dst) and self.task == "move":
            utils_logger.debug("Renaming same filesystem file")

            # just rename and return success, 1
            common.os.rename(src, dst)
            self.signals.progress.emit(self.job_id, 100)
            self.signals.finished.emit(self.job_id)
            return 1

        else:
            # prepare file objects for read/write
            with open(src, 'rb') as fsrc:
                with open(dst, 'wb') as fdst:
                    if self.size > 0:
                        return self._copyfileobj_readinto(fsrc, fdst, length=min(1048576, self.size))
                    # copy files with 0 sizes
                    return self._copyfileobj(fsrc, fdst)

    def copy(self, src, dst):
        """ rename folders and prepare files for copying """
        if common.os.path.isdir(dst):
            dst = common.os.path.join(dst, common._basename(src))
        done = self._copyfile(src, dst)
        if not done:
            # clean up incomplete dst file

            utils_logger.debug(f"Deleting incomplete file '{dst}'")
            delete_file(dst)
        return done

    def move(self, src, dst):
        """ copy then delete when done """
        done = self.copy(src, dst)
        if done:
            # delete source file only on success
            utils_logger.debug(f"File moved. Deleting source file '{src}'")
            delete_file(src)
            # try removing folder
            remove_folder(common.os.path.dirname(src))


class Thread(QThread):
    """
    run `func` in QThread
    """
    __slots__ = ("func", "args", "kwargs")
    results = common.pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.setTerminationEnabled(1)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        try:
            utils_logger.debug("Threaded function started")
            finished = self.func(*self.args, **self.kwargs)
            utils_logger.debug("Threaded function finished")
            self.results.emit(finished)
        except Exception as e:
            utils_logger.error(f"Error running function in thread: {str(e)}")


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
    new_user = common.pyqtSignal(tuple)

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
        utils_logger.debug("Deleting widgets in layout")
        while layout.count():
            child = layout.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                close_window(child.layout())
        utils_logger.debug("Done deleting widgets")


def start_file(filename):
    """
    open file using the default app
    """
    common.os.startfile(filename)


def file_exists(src, dst) -> bool:
    """ compare file properties """
    if common.os.path.isdir(dst):
        dst = common.os.path.join(dst, common._basename(src))
    if common.os.path.exists(dst):
        # return (common.os.path.getsize(src) == common.os.path.getsize(dst))
        return True
    return False


def same_filesystem(src, dst) -> bool:
    if common.os.path.commonprefix((src, dst)):
        return True
    return False


def delete_file(filename):
    """
    permanently delete a file
    """
    try:
        common.os.unlink(filename)
    except Exception:
        pass


def remove_folder(folder):
    """ delete empty folder """
    try:
        common.os.rmdir(folder)
        utils_logger.debug(f"Dir removed: '{folder}'")
    except Exception:
        utils_logger.error("Cannot remove dir, not empty")
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
    for entry in common.os.scandir(folder):
        try:
            full_path = entry.path
            # avoid listing folder-info files
            if entry.is_file() and not common.isSysFile(full_path):
                size = common.os.path.getsize(full_path)
                ext = common.os.path.splitext(full_path)[-1] or "without extensions"
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


def get_folders(path: str) -> list:
    """
    return all recursive folders in path
    return empty folder if path doesn't exist
    """

    folders = []
    if common.os.path.exists(path):
        for folder, subfolders, files in common.os.walk(path):
            if files:
                folders.append(folder)
        # folders.sort()
    return folders


def get_files_folders(path: str):
    """ return a sorted list of files first and lastly folders """
    items = []
    for entry in common.os.scandir(path):
        if entry.is_file():
            # put files at the beginning
            items.insert(0, entry.path)
        else:
            # put folders at the end
            items.append(entry.path)
    return items
