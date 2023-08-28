__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"

from typing import Generator
import os
import time
import socket


file_excludes = {"AlbumArtSmall.jpg", "Folder.jpg", "desktop.ini"}


def start_file(filename):
    """
        open file using the default app
    """
    try:
        os.startfile(filename)
    except Exception as e:
        print("[Error Opening File]", e)


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
    os.unlink(filename)


def convert_bytes(num: int) -> str:
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

    for entry in os.scandir(folder):
        if entry.is_file():
            _, ext = os.path.splitext(entry.name)
            ext = ext.strip(".").upper() + " File"
            stats = entry.stat()
            datec = time.ctime(stats.st_ctime)
            size = convert_bytes(stats.st_size)
            yield entry.name, datec, ext, size


def get_folders(path: str) -> list:
    """
        return all recursive folders in a path
    """

    folders = []
    for folder, subfolders, files in os.walk(path):
        if files:
            folders.append(folder)
    folders.sort()
    return folders
