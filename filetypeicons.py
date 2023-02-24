""" module for getting file icons assc'd with their file extensions """
import win32ui
import win32gui
import win32con
import win32api
from win32com.shell import shell, shellcon
from PIL import Image


def get_icon(PATH, size: str = None):
    """
    return an icon associated with file extension in 'PATH'
    rtype: PIL.Image
    """
    if size is None:
        # set default size
        size = "large"
    # flags
    SHGFI_ICON = shellcon.SHGFI_ICON
    SHGFI_ICONLOCATION = 0x000001000

    if size == "small":
        SHIL_SIZE = shellcon.SHGFI_SMALLICON
    elif size == "large":
        SHIL_SIZE = shellcon.SHGFI_LARGEICON
    else:
        raise TypeError("Invalid argument for 'size'. Must be equal to 'small' or 'large'")

    # get file info
    ret, info = shell.SHGetFileInfo(PATH, 0, SHGFI_ICONLOCATION | SHGFI_ICON | SHIL_SIZE)
    hIcon, iIcon, dwAttr, name, typeName = info
    # print(info)
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    # creating a destination memory DC
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    hbmp = win32ui.CreateBitmap()  # create bitmap
    hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_x)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(hbmp)
    try:
        hdc.DrawIcon((0, 0), hIcon)  # write icon to memory created earlier
        win32gui.DestroyIcon(hIcon)  # release icon

        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)  # raw icon data
        img = Image.frombuffer(
            "RGBA",  # transparent image
            (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
            bmpstr, "raw", "BGRA", 0, 1
        )
        # return PIL Image
        return img
    except win32ui.error:
        # draw icon fails
        return


if __name__ == "__main__":
    im = get_icon(r"C:\Users\Windows 10 Pro\Documents\GSAT-19E.tex", size="small")
    if im:
        im.show()

# Linux
"""
import mimetypes

import gio
import gtk

def get_icon_path(extension, size=32):
    type_, encoding = mimetypes.guess_type('x.' + extension)
    if type_:
        icon = gio.content_type_get_icon(type_)
        theme = gtk.icon_theme_get_default()
        info = theme.choose_icon(icon.get_names(), size, 0)
        if info:
            return info.get_filename()
"""
# GTK3
"""
from gi.repository import Gtk, Gio

def get_icon_path(mimetype, size=32):
    icon = Gio.content_type_get_icon(mimetype)
    theme = Gtk.IconTheme.get_default()
    info = theme.choose_icon(icon.get_names(), size, 0)
    if info:
        print(info.get_filename())
"""
