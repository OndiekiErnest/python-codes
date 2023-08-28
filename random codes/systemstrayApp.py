from tkinter import Tk
import pystray
from PIL import Image

# create an instance of the tkinter window
window = Tk()
# set window initial size
window.geometry("400x300+0+100")
# window.overrideredirect(True)
# window.attributes("-fullscreen", True)


# function to quit the window completely
def quit_window(icon, item):
    # stop icon
    icon.stop()
    window.destroy()


# function to show the window again
def show(icon, item):
    icon.stop()
    window.deiconify()


# on left-click
def on_click(icon, item):
    pass


# function to hide the window to the system taskbar
def hide():
    # hide the tkinter window
    window.withdraw()
    # get the icon running in the system taskbar
    image = Image.open("C:\\Users\\code\\Pictures\\add_121935.png")

    # create options/items
    option1 = pystray.MenuItem("Show", show, default=1)
    option2 = pystray.MenuItem("Quit", quit_window)
    option3 = pystray.MenuItem("Click", on_click)

    # create a menu of options
    menu = pystray.Menu(option1, option2, option3)
    # create the icon
    icon = pystray.Icon("Lazy_Selector", image,
                        "Lazy Selector", menu)
    # icon._status_icon.connect('popup-menu', self._on_status_icon_popup_menu)
    icon.run()


# hide window when user presses close
window.wm_protocol("WM_DELETE_WINDOW", hide)
# start application main loop
window.mainloop()
