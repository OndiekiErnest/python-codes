from tkinter import*

wn = Tk()
wn.iconbitmap(default=r"C:\\Users\\code\\Pictures\\icons\\musicapp.ico")
#wn.resizable(width=False,height=False)
wn.title("Mplayer")
wn.maxsize(400, 508)
wn.geometry('400x506+950+2')
wn.config(bg="dark green")
statusbar = Label(wn, bg="dark green", 
				text=":"*50, 
				fg="white", font=("arial",10,'bold'),width=49)
statusbar.place(y=481,x=0)
frm = Frame(wn, bg="gray14",width=199,height=480)
frm.place(y=0,x=1)

forimg = PhotoImage(file="C:\\Users\\code\\Pictures\\forward.png")
bacimg = PhotoImage(file="C:\\Users\\code\\Pictures\\back.png")
stoimg = PhotoImage(file="C:\\Users\\code\\Pictures\\stop.png")
file_image = PhotoImage(file="C:\\Users\\code\\Pictures\\background_music.png")

artist_label = Label(frm,relief=GROOVE,bg="dark green",fg="white",
						font=("arial",8,'italic bold'),text="Artist:",width=32,anchor=W)
artist_label.place(x=0,y=0)

image_label = Label(frm,relief=GROOVE,bg="white")
image_label.place(x=28,y=150)
image_label.config(image=file_image,width=140,height=140)

back_btn = Button(frm, image=bacimg).place(y=440,x=40)
stop_btn = Button(frm, image=stoimg).place(y=440,x=80)
forward_btn = Button(frm, image=forimg).place(y=440,x=120)
            #Frame 2
frm2 = Frame(wn,width=196,height=480)
frm2.place(y=0,x=202)
playlist_label = Label(frm2,text="--Playlist--",relief=GROOVE,width=27,
						bg="dark green", fg="white",font=("arial",10,'italic bold'))
playlist_label.place(x=0,y=0)
songs_list = Listbox(frm2, bg="gray14",width=31,height=31,fg="white", font=("arial",8,'italic bold'))
songs_list.place(x=3,y=24)
songs_list.insert(0,"01 Songs posted here")
playlist_label = Label(frm2,text="Duration:",relief=GROOVE,width=31,anchor=W,
						bg="dark green", fg="white",font=("arial",8,'italic bold'))
playlist_label.place(x=1.5,y=460)

menubar = Menu(wn)
wn.config(menu=menubar)
submenu = Menu(menubar,tearoff=0)
menubar.add_cascade(label="File", menu=submenu)
submenu.add_command(label="Open Folder")



submenu = Menu(menubar,tearoff=0)
menubar.add_cascade(label="Help", menu=submenu)
submenu.add_command(label="About")


wn.mainloop()