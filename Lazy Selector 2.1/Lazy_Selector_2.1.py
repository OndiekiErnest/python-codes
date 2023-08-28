

from tkinter import Tk, Label, Frame, Button, Canvas, PhotoImage, W, Menu, CENTER, SE
from tkinter.ttk import Progressbar
import random, os, sys
from mutagen.mp3 import MP3
from deque import Deque
from tkinter.messagebox import askokcancel, showinfo
from tkinter.filedialog import askdirectory, askopenfilenames
from configparser import ConfigParser
from pygame import mixer, init


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Player:
	"""Plays mp3 audio files in shuffle mode
	win is tkinter's toplevel widget Tk"""
	_CONFIG = ConfigParser()
	_CONFIG.read(BASE_DIR+"\\lazylog.ini")
	BG = _CONFIG["theme"]["bg"]
	FG = _CONFIG["theme"]["fg"]
	MN = BG
	def __init__(self, win):
		init()
		self._root = win
		self._XSPD = 0
		self._YSPD = 0
		self._W = 303
		self._H = 13
		self.total_length = ""
		self._all_files = []
		self.num = 0
		self._prev_f = 44100
		self._time = ""
		self._play_btn_text = ""
		self._title_txt = ""
		self._repeat_image = PhotoImage(file=os.path.join(BASE_DIR, "shuffle_RGB.png"))
		self._start = 0
		self._play_btn_command = None
		self._play_prev_command = None
		self._play_next_command = None
		self._repeat_com = self._enable_repeat
		self._active_repeat = False
		self._files_selected = False
		self._stored = Deque()
		self.time_cnt = "after#0"
		self.cnt = "after#0"

		self.menubar = Menu(self._root)
		self._root.config(menu=self.menubar)
		self._menu(self.menubar,"File","Open Folder",com=self._refresher)
		self.submenu.add_command(label="Add To Queue",command=self._select_fav)

		self._menu(self.menubar,"Themes","Orange",com = lambda: self._update_color("DarkOrange3", "black", "centered_RGB.png"))
		self.submenu.add_command(label="Pink",command=lambda: self._update_color("DeepPink3", "black", "cropped_RGB.png"))
		self.submenu.add_command(label="Blue",command=lambda: self._update_color("RoyalBlue3", "black", "centered_RGB.png"))
		self.submenu.add_command(label="Brown",command=lambda: self._update_color("brown4", "gray91", "cropped_RGB.png"))
		self.submenu.add_command(label="Gray",command=lambda: self._update_color("gray30", "gray91", "small_RGB.png"))

		self._menu(self.menubar, "Help","About",com=self._about)
		self._init()
		self._refresher()

	def _init(self):
		self._root.title("Lazy Selector".ljust(34))
		self._root.geometry("310x90+"+Player._CONFIG["window"]["position"])
		self._root.resizable(0,0)
		self._root.config(bg=Player.MN)
		self._root.iconbitmap(default=BASE_DIR+"\\musicapp.ico")
		self._root.tk_focusFollowsMouse()
		self._root.wm_protocol("WM_DELETE_WINDOW",self._kill)

		self._progress_frame = Frame(self._root, width=306, height=2)
		self._progress_frame.place(x=2,y=64)

		self._progress_bar = Progressbar(self._progress_frame, orient="horizontal",length=308,mode="determinate")
		self._progress_bar.place(x=-2,y=-3)

		self._current_time = Label(self._root,padx=0,text=self._time,
									bg=Player.BG,font=('arial',9,'bold'),fg=Player.FG,width=5)
		self._current_time.place(x=41,y=68)

		self._title = Label(self._root, pady=0,bg=Player.BG, text=self._title_txt,
							font=('arial',7,'bold'), fg=Player.FG, width=50)
		self._title.place(x=1, y=1)

		self._duration_label = Label(self._root, padx=0,
								bg=Player.BG,font=("arial",9,"bold"),fg=Player.FG,width=5)
		self._duration_label.place(x=227,y=68)

		self._shuffle = Button(self._root,command=self._play,text="SHUFFLE",padx=10,
								bg=Player.BG,fg=Player.FG,font=("arial",15,"bold"))
		self._shuffle.place(x=91,y=18)

		self._previous_btn = Button(self._root,padx=5,bg=Player.BG,fg=Player.FG, command = self._play_prev_command,
									font=("arial",7,"bold"),width=5,height=1,text="I<<")
		self._previous_btn.place(x=80,y=68)


		self._play_btn = Button(self._root,padx=5,bg=Player.BG,text=self._play_btn_text,command=self._play_btn_command,
								fg=Player.FG,font=("arial",7,"bold"),width=5,height=1)

		self._play_btn.place(x=130,y=68)

		self._next_btn = Button(self._root,padx=5,bg=Player.BG,text=">>I", command = self._play_next_command,
								fg=Player.FG,font=("arial",7,"bold"),width=5,height=1)

		self._next_btn.place(x=180,y=68)

		self._left_display = Label(self._root,height=37,width=40)
		self._left_display.place(x=41,y=18)

		self._right_display = Label(self._root,height=37,width=40)
		self._right_display.place(x=222,y=18)
		self._update_speakers(Player._CONFIG["theme"]["photo"])


		self._repeat_btn = Button(self._root,pady=0,padx=0,bg=Player.BG,command=self._repeat_com,width=20,height=15,
			relief="flat",font=("arial",6,"bold"),anchor=W,image=self._repeat_image)
		self._repeat_btn.place(x=3,y=68)



	def _refresher(self):
		self._songspath = askdirectory(title="Choose a Music Folder with MP3 Audio Files")
		try:
			file = Player._CONFIG["files"]["folder"] #try getting the previous folder
		except KeyError:
			Player._CONFIG.set("files","folder",self._songspath) #failed, set the folder opened
			file = Player._CONFIG["files"]["folder"] # get the folder

		if (file == self._songspath) and (self._all_files != []):
			#don't update the songs list
			pass
		else:
			#update
			try:
				self._all_files = os.listdir(self._songspath)

			except FileNotFoundError:
				if (file != "") and (self._all_files == []): # if log file isn't empty and songs list is empty
					self._songspath = file
					self._all_files = os.listdir(self._songspath)
				elif (self._songspath == "") and (self._all_files != []): # if no directory was chosen and songs list isn't empty
					self._songspath = file
				else:
					if askokcancel("Lazy Selector",
									"First time requires that you select a folder!\n    Do you want to select a folder again?"):
						self._refresher()
					else:
						sys.exit()
						self._root.destroy()
		Player._CONFIG.set("files","folder",self._songspath)

	def _loader(self):
		for i in range(len(self._all_files)):
			self.randnum = random.randint(0, len(self._all_files)-1)
			self._extract = self._all_files[int(self.randnum)]
			if self._extract.endswith('.mp3'):
				song = os.path.join(self._songspath, self._extract)
				try:
					self._freq, self.duration, mode = self._info(song)
				except Exception as e:
					self._all_files.remove(self._extract)
					continue
			else:
				self._all_files.remove(self._extract)
				continue
			self._all_files.remove(self._extract)
			self.num +=1
			break
		try:
			return song
		except Exception as e:
			str_error = str(e).split()
			if ("'song'" in str_error) and (self.num == 0):
				return "mp3"
			else:
				return False


	def _select_fav(self):

		self._loaded_files = askopenfilenames(filetypes=[("MP3 files","*.mp3")])
		if len(self._loaded_files) != 0:
			self._files_selected = True
			self._loaded_files = [i for i in self._loaded_files]
			for audio in self._loaded_files:
				song = os.path.basename(audio)
				if song in self._all_files:
					self._all_files.remove(song)


	def _load_files(self):

		for audio in self._loaded_files:
			song = audio
			try:
				self._freq, self.duration, mode = self._info(self._song)
			except Exception:
				self._loaded_files.remove(self._extract)
				continue
			self._loaded_files.remove(audio)
			return song
			break

	def _takeover(self):
		self._start = 0
		if self._active_repeat:
			self._root.after_cancel(self.time_cnt)
			self._mixer(self._song, self._freq)
			self.cnt = self._root.after(self.after, self._takeover)
			self._set_uptime()
		else:
			self._play()


	def _play(self):
		self._shuffle["state"] = "disabled"
		self._start = 0
		self._play_btn_text = "PAUSE"
		self._play_prev_command = lambda: self._play_prev()
		self._play_btn_command = self._stop_play
		self._root.after_cancel(self.time_cnt)

		if not self._files_selected:
			self._song = self._loader()

		elif self._files_selected:
			self._song = self._load_files()
			if len(self._loaded_files) == 0:
				self._files_selected = False
		if self._song and self._song != "mp3":

			self._title_txt = os.path.splitext(os.path.basename(self._song))[0]

			self._freq, self.duration, mode = self._info(self._song)
			self._mixer(self._song,self._freq)
			self._root.after_cancel(self.cnt)
			self.after = int(round(self.duration)*1000)
			if mixer.music.get_busy():
				self.cnt = self._root.after(self.after, self._takeover)

			else:
				self.cnt = self._root.after(1,self._takeover)
			self._root.update()
			self._updating()
			self._set_uptime()

		if self._song == "mp3":
			showinfo("Lazy Selector", "The selected Folder has no MP3 files.\n      Choose a different Folder.")
			self._refresher()
			self._song = self._loader()

		elif not self._song:
			self._root.after_cancel(self.cnt)
			showinfo("Lazy Selector",
					"     All folder songs have played. Select another folder to play"\
					"\nClick Cancel in the next dialog to repeat the just ended folder.")
			self._refresher()
			self._song = self._loader()
		self._root.update()
		self._shuffle["state"] = "normal"

	def _updating(self):
		mins, secs = divmod(self.duration, 60)
		self.total_length = f"{round(mins):02}:{round(secs):02}"

		if len(self._stored) == 7:
			self._stored.delete_last()
			self._stored.insert_first(self._song)
		elif len(self._stored) < 7:
			self._stored.insert_first(self._song)

		self._update_labels(self._title_txt,self.total_length)
		self._previous_btn["command"] = self._play_prev_command
		self._play_btn["text"] = self._play_btn_text
		self._play_btn["command"] = self._play_btn_command

		self._prev_song = self._stored.first()


	def _play_prev(self, prev=True):
		self._play_btn_text = "PAUSE"
		self._play_btn_command = self._stop_play
		self._play_next_command = lambda: self._play_prev(prev=False)
		self._next_btn["command"] = self._play_next_command
		self._root.after_cancel(self.cnt)
		self._root.after_cancel(self.time_cnt)
		self._root.update()
		self._start = 0
		if prev:
			self._previous_btn["state"] = "disabled"
			try:
				if not self._prev_song.next_.element_ == None:
					self._song = self._prev_song.next_.element_
					self._prev_song = self._prev_song.next_
			except Exception as e:
				self._song = self._song
		else:
			self._next_btn["state"] = "disabled"
			try:
				if not self._prev_song.prev.element_ == None:
					self._song = self._prev_song.prev.element_
					self._prev_song = self._prev_song.prev
			except Exception as e:
				self._song = self._song

		self._freq, self.duration, mode = self._info(self._song)
		self._mixer(self._song, self._freq)
		self._title_txt = os.path.splitext(os.path.basename(self._song))[0]
		mins, secs = divmod(self.duration, 60)
		self.total_length = f"{round(mins):02}:{round(secs):02}"
		self._update_labels(self._title_txt,self.total_length)
		self._play_btn["text"] = self._play_btn_text
		self._play_btn["command"] = self._play_btn_command
		self.cnt = self._root.after(round(self.duration)*1000,self._takeover)

		self._set_uptime()
		self._root.update()
		self._previous_btn["state"] = "normal"
		self._next_btn["state"] = "normal"


	def _enable_repeat(self):

		self._repeat_image = PhotoImage(file=os.path.join(BASE_DIR, "repeat_RGB.png"))
		self._repeat_com = self._disable_repeat
		self._repeat_btn["image"] = self._repeat_image
		self._repeat_btn["command"] = self._repeat_com
		self._active_repeat = True

	def _disable_repeat(self):
		self._repeat_image = PhotoImage(file=os.path.join(BASE_DIR, "shuffle_RGB.png"))
		self._repeat_com = self._enable_repeat
		self._repeat_btn["image"] = self._repeat_image
		self._repeat_btn["command"] = self._repeat_com
		self._active_repeat = False

	def _update_speakers(self, photo):
		# from PIL import Image
		# i = Image.open("repeat.png")
		# i.thumbnail((20,30), Image.ANTIALIAS)
		# i.save("repeat_RGB.png")
		self.speaker = PhotoImage(file=os.path.join(BASE_DIR, photo))
		self._left_display.config(image = self.speaker)
		self._right_display.config(image = self.speaker)

	def _mixer(self, s, f):
		if not self._prev_f == f:
			mixer.quit()
		mixer.pre_init(frequency=f,buffer=1024,allowedchanges=0)
		mixer.init()
		mixer.music.load(s)
		mixer.music.play()
		self._prev_f = f

	def _kill(self):

		if mixer.music.get_busy():
			if askokcancel("Lazy Selector","Music is still playing.\n      Quit Anyway?"):
				try:
					Player._CONFIG.set("window","position",f"{self._root.winfo_x()}+{self._root.winfo_y()}")
					with open(BASE_DIR+"\\lazylog.ini","w") as f:
						Player._CONFIG.write(f)
				except Exception as er:
					pass

				mixer.quit()
				self._root.destroy()
				sys.exit()
		else:
			try:
				with open(BASE_DIR+"\\lazylog.ini","w") as f:
					Player._CONFIG.write(f)
			except Exception as er:
				pass
			self._root.destroy()
			sys.exit()

	def _info(self, s):
		"""Returns tuple(freq,duration,mode,title)"""
		songdetails = MP3(s)
		return songdetails.info.sample_rate, songdetails.info.length, songdetails.info.mode

	def _convert(self, text):

		elem = [i if ord(i) < 65535 else "." for i in text]

		return "".join(elem)

	def _update_labels(self,song,dur):
		if self._title_txt == "MUSIC PAUSED" or len(self._title_txt) <= 58:
			self._title_txt_anchor = CENTER
			self._title["anchor"] = self._title_txt_anchor
		elif len(self._title_txt) > 58:
			self._title_txt_anchor = W
			self._title["anchor"] = self._title_txt_anchor
		self._title["text"] = self._convert(song)
		self._duration_label["text"] = dur

	def _menu(self,master,top,name,com=None):
		self.submenu = Menu(master,tearoff=0)
		self.menubar.add_cascade(label=top, menu=self.submenu)
		self.submenu.add_command(label=name,command=com)

	def _about(self):
		"""Shows information about the player"""
		showinfo("Lazy Selector",
				"Lazy Selector\nVersion: 2.1\n\n      An audio player that reads MP3 files only"+\
				"\nThe previous button goes back 7 previous songs\n\nDeveloped by Ernesto")

	def _update_color(self, bg, fg, img):
		Player.BG = bg
		Player.FG = fg
		Player.MN = bg
		Player._CONFIG.set("theme","bg",Player.BG)
		Player._CONFIG.set("theme","fg",Player.FG)
		Player._CONFIG.set("theme","photo",img)
		self._init()
		self._update_labels(self._title_txt,self.total_length)

	def _stop_play(self):
		self._play_btn["state"] = "disabled"
		self._play_btn_text = "PLAY"
		self._play_btn_command = self._unpause
		self._root.after_cancel(self.time_cnt)
		self._root.after_cancel(self.cnt)
		mixer.music.pause()
		self._title["anchor"] = CENTER
		self._title["text"] = "MUSIC PAUSED"
		self._play_btn["text"] = self._play_btn_text
		self._play_btn["command"] = self._play_btn_command
		self._root.update()
		self._play_btn["state"] = "normal"

	def _unpause(self,event=None):
		"""Resumes playback"""
		self._play_btn["state"] = "disabled"
		self._play_btn_command = self._stop_play
		self._play_btn_text = "PAUSE"
		self._title["anchor"] = self._title_txt_anchor
		self._title["text"] = self._title_txt
		self._play_btn["text"] = self._play_btn_text
		self._play_btn["command"] = self._play_btn_command
		mixer.music.unpause()
		self.cnt = self._root.after(((int(self.duration)-int(self._start))*1000),self._takeover)
		self._set_uptime()
		self._root.update()
		self._play_btn["state"] = "normal"

	def _set_uptime(self):
		"""Updates current time"""
		self._progress_bar["maximum"] = self.duration
		mins, secs = divmod(self._start, 60)
		self._time = f"{round(mins):02}:{round(secs):02}"
		self._current_time.config(text=self._time)
		self._progress_bar.config(value=self._start)
		self._progress_bar.update()
		self._start += 1
		self.time_cnt = self._root.after(1000,self._set_uptime)
		self._root.update()



tk = Tk()
p = Player(tk)
tk.mainloop()