__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"
import os
import socket
import logging
from PyQt5.QtCore import QObject, pyqtSignal
from ftplib import FTP_TLS, error_perm


logging.basicConfig(level=logging.DEBUG)
common_logger = logging.getLogger(__name__)
common_logger.debug(f"Initializing {__name__}")


BR_PORT = 12001
BR_SIGN = ")tr@P("
file_excludes = {"AlbumArtSmall.jpg", "Folder.jpg", "desktop.ini"}
other_file_excludes = ("AlbumArt_", "~")
CERTF = os.path.abspath(os.path.join(os.path.dirname(__file__), 'keycert.pem'))
OS_SEP = os.sep

# serve using this machine's IP
MACHINE_IP = socket.gethostbyname(socket.gethostname())


class BasicSignals(QObject):

    error = pyqtSignal(str)
    success = pyqtSignal(str)


def ftp_tls() -> FTP_TLS:
    """ create FTP_TLS instance and return it """
    ftp = FTP_TLS()
    ftp.certfile = CERTF
    ftp.encoding = "utf-8"
    return ftp


def _basename(path):
    """ strip trailing slash and return basename """
    # A basename() variant which first strips the trailing slash, if present.
    # Thus we always get the last component of the path, even for directories.
    # borrowed from shutil.py
    sep = os.path.sep + (os.path.altsep or '')
    return os.path.basename(path.rstrip(sep))


def isSysFile(path) -> bool:
    """ is a sys file based on pre-defined criteria """
    filename = _basename(path)
    return (filename.startswith(other_file_excludes) or (filename in file_excludes))


def scan_folder(path: str):
    """ Generator: return a list of folders """
    if os.path.exists(path):
        for entry in os.scandir(path):
            if entry.is_dir():
                # get the path
                yield entry.path
    yield


def to_bytes(value: str) -> float:
    """ convert a str (of the form, 'size unit') to float for sorting """
    try:
        size, unit = value.split(" ")
        size = float(size)
        if unit == "GB":
            return size * 1073741824
        elif unit == "MB":
            return size * 1048576
        elif unit == "KB":
            return size * 1024
        else:
            return size
    except Exception:
        return 0


def convert_bytes(num: int) -> str:
    """ format bytes to respective units for presentation (max GB) """
    try:
        if num >= 1073741824:
            return f"{round(num / 1073741824, 2)} GB"
        elif num >= 1048576:
            return f"{round(num / 1048576, 2)} MB"
        elif num >= 1024:
            return f"{round(num / 1024, 2)} KB"
        else:
            return f"{num} Bytes"
    except Exception:
        return "NaN"


def get_files(folder: str):
    """
    return the file and its stats
    """

    for entry in os.scandir(folder):
        # avoid listing folder-info files
        if entry.is_file() and not isSysFile(entry.path):
            # get the needed details and return them
            yield get_file_details(entry.path)


def get_file_details(filename: str):
    """
    return file name, folder, ext, size
    """
    name, folder = _basename(filename), os.path.dirname(filename)
    ext = os.path.splitext(name)[-1]
    ext = ext.strip('.').upper()
    size = os.path.getsize(filename)
    return name, folder, ext, size
