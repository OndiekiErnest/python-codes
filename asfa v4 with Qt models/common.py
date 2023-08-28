__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"
import os


BR_PORT = 12001
BR_SIGN = ")tr@P("
file_excludes = {"AlbumArtSmall.jpg", "Folder.jpg", "desktop.ini"}
other_file_excludes = ("AlbumArt_", "~")
CERTF = os.path.abspath(os.path.join(os.path.dirname(__file__), 'keycert.pem'))


def to_bytes(value: str) -> float:
    """ convert a str (of the form, 'size unit') to float for sorting """
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
