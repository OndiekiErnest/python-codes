from tkinter import Tk, Frame, Label
from tkinter.ttk import Notebook

root = Tk()  # list_frame
root.title("TAB")
# create controls in controls_frome; place it in list_frame

# initialize notebook
book = Notebook(root, height=100, width=200)
# create frames to group other widgets
# widget for local
local = Frame(book)  # local_listview frame
# widget for online
online = Frame(book)  # streams_listview frame

# adding/creating tabs
book.add(local, text="Local")
book.add(online, text="Stream")
book.pack(fill="both")

# placing widgets in tabs (frames)
# the frames can hold any widget
local_msg = Label(local, text="Offline content here")  # listbox and scrollbar
online_msg = Label(online, text="Online content here")  # listbox and scrollbar
local_msg.pack()
online_msg.pack()

root.mainloop()

# import youtubesearchpython as ys
