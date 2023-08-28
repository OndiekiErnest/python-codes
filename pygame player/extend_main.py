from tkinter import Tk, Listbox, Button, PhotoImage, Label, FLAT, Radiobutton, Variable
from tkinter.ttk import LabelFrame, Scrollbar
import time, sys
from configparser import ConfigParser

CONFIG = ConfigParser()
CONFIG.read("lazylog.ini")
def main_win():

	"""Sets the entrance window properties
	
	"""
	"""---------Widgets----------"""
	global win
	win = Tk()
	win.title("Settings")
	win.geometry("380x125+450+250")
	win.resizable(0,0)
	win.iconbitmap(default="cat_head.ico")
	win.config(bg="gray45")
	win.tk_focusFollowsMouse()
	win.wm_protocol("WM_DELETE_WINDOW",kill)



	# from PIL import Image
	# i = Image.open("favourites.png")
	# i.thumbnail((24,24), Image.ANTIALIAS)
	# i.save("RGB_fav.png")
	list_image = PhotoImage(file="RGB_list.png")
	playlist_image = Label(win,width=24,height=22, image=list_image)
	playlist_image.place(x=2,y=5)

	playlist_btn = Button(win, relief=FLAT, width=21, text="PLAYLIST",font=("bold",9),command=playlist_add)
	playlist_btn.place(x=32,y=5)

	"""-------------Favourites-----------"""
	fav_image = PhotoImage(file="RGB_fav.png")
	favorites_image = Label(win,width=24,height=22, image=fav_image)
	favorites_image.place(x=350,y=5)

	favorites_btn = Button(win, relief=FLAT, width=21, text="FAVOURITE SONGS",font=("bold",9),command=favourites_add)
	favorites_btn.place(x=191,y=5)

	"""-------------Themes Frame-------------"""
	themes_frame = LabelFrame(win,text="Themes",width=188,height=50)
	themes_frame.place(x=5,y=35)

	MODES = [("Blue","Blue"),
		("Green","Green"),
		("Pink","Pink"),
		("Brown","Brown"),
		("Dark","Dark"),
		("Gray","Gray"),
		("Gold","Gold")
	]
	global v
	v = Variable()
	v.set(CONFIG["theme"]["current"])
	global mode
	for text, mode in MODES:
		radio = Radiobutton(themes_frame,text=text,variable=v,value=mode,padx=0, 
				bg="gray45",activebackground="lime green",selectcolor="lime green")
		radio.pack(anchor="w",side="right")

	win.mainloop()

def get_variable(v):

	return v.get()
	win.after(2000, get_variable)

def kill():

	CONFIG.set("theme","current",get_variable(v))
	with open("lazylog.ini", "w") as f:
		CONFIG.write(f)
	sys.exit()
	win.destroy()

def convert(text):

	elem = [i if ord(i) < 65535 else "." for i in text]

	return "".join(elem)


def list_view(title):

	"""Displays all songs in the current directory
	
	
	"""
	global list_box, now_playing_label, list_win
	list_win = Tk()
	list_win.title(title)
	list_win.iconbitmap(default="cat_head.ico")
	list_win.geometry("500x700+855+4")
	list_win.resizable(0,0)

	
	list_box = Listbox(list_win,bg="gray60",width=80,height=44,selectmode="extended")
	scroll_bar = Scrollbar(list_win, orient="vertical",command=list_box.yview)
	list_box.config(yscrollcommand=scroll_bar.set)

	now_playing_label = Label(list_win,bg="gray12",fg="gray91",font=("sans",8),anchor="center",width=50)
	now_playing_label.pack(side="top",fill="x")
	scroll_bar.pack(side="right",fill="y")
	list_box.pack(pady=5)

def update_label():
	global c
	now_playing_label["text"] = list_box.get("anchor")
	c = list_win.after(1000,update_label)

def kill_():
	list_win.after_cancel(c)
	list_win.destroy()

def favourites_add():
	list_view("Favourite Songs")
	update_label()
	list_win.wm_protocol("WM_DELETE_WINDOW",kill_)
	import os
	path = "C:\\Users\\code\\Music\\DAMN"
	for item in os.listdir(path):
		list_box.insert("end",convert(item))
	list_win.mainloop()

def playlist_add():
	list_view("All Songs")
	update_label()
	list_win.wm_protocol("WM_DELETE_WINDOW",kill_)
	import os
	path = "C:\\Users\\code\\Music\\DAMN"
	for item in os.listdir(path):
		list_box.insert("end",convert(item))
	list_win.mainloop()



if __name__ == '__main__':
	main_win()
