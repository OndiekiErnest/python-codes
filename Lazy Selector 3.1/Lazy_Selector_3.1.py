
from ttkthemes import ThemedStyle
from tkinter import Tk, Frame, PhotoImage, W, Menu, CENTER, SE, DoubleVar
from tkinter.ttk import Style, Scale, Label, Button
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
		self._progress_variable = DoubleVar()
		self.total_length = ""
		self._all_files = []
		self.num = 0
		self._start = 0
		self._paused = False
		self._prev_f = 44100
		self._time = ""
		self._play_btn_text = ""
		self._title_txt = ""
		self._repeat_image = PhotoImage(file=os.path.join(BASE_DIR, "shuffle_RGB.png"))
		self._play_btn_command = None
		self._play_prev_command = None
		self._play_next_command = None
		self._active_repeat = False
		self._files_selected = False
		self._slider_above = False
		self._stored = Deque()
		self.time_cnt = "after#0"

		self.menubar = Menu(self._root) 
		self._root.config(menu=self.menubar)
		self.file_menu = Menu(self.menubar,tearoff=0, fg=Player.FG, bg=Player.BG)
		self.menubar.add_cascade(label="File", menu=self.file_menu)
		self.file_menu.add_command(label="Open Folder",command=self._refresher)
		self.file_menu.add_command(label="Add To Queue",command=self._select_fav)

		self.theme_menu = Menu(self.menubar,tearoff=0, fg=Player.FG, bg=Player.BG)
		self.menubar.add_cascade(label="Themes", menu=self.theme_menu)
		self.theme_menu.add_command(label="White",command=lambda: self._update_color("white smoke", "black", "gray_RGB.png"))
		self.theme_menu.add_command(label="Gray",command=lambda: self._update_color("gray30", "white", "gray_RGB.png"))
		self.theme_menu.add_command(label="Blue",command=lambda: self._update_color("RoyalBlue3", "black", "sb_RGB.png"))
		self.theme_menu.add_command(label="Pink",command=lambda: self._update_color("DeepPink3", "white", "bw_RGB.png"))
		self.theme_menu.add_command(label="Orange",command=lambda: self._update_color("DarkOrange3", "black", "ob_RGB.png"))

		self.about_menu = Menu(self.menubar,tearoff=0, fg=Player.FG, bg=Player.BG)
		self.menubar.add_cascade(label="Help", menu=self.about_menu)
		self.about_menu.add_command(label="About",command=self._about)
		self.about_menu.add_command(label="Switch Slider",command=self._change_place)
		self._init()
		self._root.lift()
		self._refresher()

	def _init(self):
		
		self._root.geometry("310x110+"+Player._CONFIG["window"]["position"])
		self._root.resizable(0,0)
		self._root.iconbitmap(default=BASE_DIR+"\\musicapp.ico")
		self._root.tk_focusFollowsMouse()
		self._root.wm_protocol("WM_DELETE_WINDOW",self._kill)

		self._progress_bar = Scale(self._root,from_=0,orient="horizontal",length=304,
						cursor="hand2",variable=self._progress_variable,command=self._slide)
		self._progress_bar.place(x=1,y=92)

		self._current_time = Label(self._root,text=self._time,
									font=('arial',9,'bold'),width=5)
		self._current_time.place(x=41,y=68)

		self._title = Label(self._root, text=self._title_txt,
							font=('arial',8,'bold'), width=51)
		self._title.place(x=1, y=1)

		self._duration_label = Label(self._root,
								font=("arial",9,"bold"),width=5)
		self._duration_label.place(x=227,y=68)

		self._shuffle = Button(self._root,command=self._play,text="SHUFFLE",width=16)
		self._shuffle.place(x=91,y=20)
		
		self._previous_btn = Button(self._root,command = self._play_prev_command,width=5,text="I<<")
		self._previous_btn.place(x=80,y=68)


		self._play_btn = Button(self._root,text=self._play_btn_text,command=self._play_btn_command,width=5)
		
		self._play_btn.place(x=130,y=68)

		self._next_btn = Button(self._root,text=">>I", command = self._play_next_command,width=5)
		
		self._next_btn.place(x=180,y=68)

		self._left_display = Label(self._root,width=40)
		self._left_display.place(x=41,y=20)

		self._right_display = Label(self._root,width=40)
		self._right_display.place(x=222,y=20)
		self._update_speakers(Player._CONFIG["theme"]["photo"])
		

		self._repeat_btn = Button(self._root,command=self._onoff_repeat,width=20,image=self._repeat_image)
		self._repeat_btn.place(x=3,y=68)

	def _change_place(self):

		if self._slider_above:
			self._pb = 92
			self._controls = 68
		else:
			self._pb = 68
			self._controls = 86
		self._progress_bar.place(x=1,y=self._pb)
		self._current_time.place(x=41,y=self._controls)
		self._duration_label.place(x=227,y=self._controls)
		self._previous_btn.place(x=80,y=self._controls)
		self._play_btn.place(x=130,y=self._controls)
		self._next_btn.place(x=180,y=self._controls)
		self._repeat_btn.place(x=3,y=self._controls)
		self._root.update()
		self._slider_above = not self._slider_above

	def _update_theme(self):

		self._root.config(bg=Player.MN)
		self._progress_bar["troughcolor"] = Player.BG
		self._repeat_btn["bg"], self._repeat_btn["fg"] = Player.BG, Player.FG
		self._play_btn["bg"], self._play_btn["fg"] = Player.BG, Player.FG
		self._next_btn["bg"], self._next_btn["fg"] = Player.BG, Player.FG
		self._shuffle["bg"], self._shuffle["fg"] = Player.BG, Player.FG
		self._previous_btn["bg"], self._previous_btn["fg"] = Player.BG, Player.FG
		self._duration_label["bg"], self._duration_label["fg"] = Player.BG, Player.FG
		self._current_time["bg"], self._current_time["fg"] = Player.BG, Player.FG
		self._title["bg"], self._title["fg"] = Player.BG, Player.FG
		self.file_menu["bg"], self.file_menu["fg"] = Player.BG, Player.FG
		self.theme_menu["bg"], self.theme_menu["fg"] = Player.BG, Player.FG
		self.about_menu["bg"], self.about_menu["fg"] = Player.BG, Player.FG
 




	def _refresher(self):
		self._songspath = askdirectory(title="Choose a Music Folder with MP3 Audio Files")
		try:
			file = Player._CONFIG["files"]["folder"] #try getting the previous folder
		except KeyError:
			Player._CONFIG.set("files","folder",self._songspath) #failed, set the folder opened
			file = self._songspath # get the folder

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
		self._root.title(f"Lazy Selector - {os.path.basename(self._songspath)}".ljust(24))
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
				self._freq, self.duration, mode = self._info(audio)
			except Exception as e:
				print(e)
				self._loaded_files.remove(audio)
				continue
			self._loaded_files.remove(audio)
			return song
			song = None
			break

	def _takeover(self):
		self._progress_variable.set(0)
		if self._active_repeat:
			self._root.after_cancel(self.time_cnt)
			self.time_cnt = None
			self._start = 0
			self._mixer(self._song, self._freq)
			self._progress_bar["to"] = self.duration
			self._set_uptime(self._start)
		else:
			self._play()


		
	def _play(self):
		self._shuffle["state"] = "disabled"
		self._play_btn_text = "PAUSE"
		self._play_prev_command = lambda: self._play_prev()
		self._play_btn_command = self._stop_play

		if not self._files_selected:
			self._song = self._loader()

		elif self._files_selected:
			self._song = self._load_files()
			if len(self._loaded_files) == 0:
				self._files_selected = False
		if self._song and self._song != "mp3":
			
			self._title_txt = os.path.splitext(os.path.basename(self._song))[0]
			
			self._freq, self.duration, mode = self._info(self._song)
			self._progress_bar["to"] = self.duration
			if self.time_cnt is not None:
				self._root.after_cancel(self.time_cnt)
			self.time_cnt = None
			self._start = 0
			self._mixer(self._song,self._freq)
			self._root.update()
			self._updating()
			self._set_uptime(self._start)
			
		if self._song == "mp3":
			try:
				showinfo("Lazy Selector", f"{os.path.basename(self._songspath)} folder has no MP3 files.\n\n   Choose a different Folder.")
			except AttributeError:
				showinfo("Lazy Selector", "No folder is initialized!")
			self._refresher()
			self._song = self._loader()

		elif not self._song:
			showinfo("Lazy Selector",
					"                          All songs have played."\
					"\n\nClick Cancel in the next dialog to repeat the just ended folder.")
			self._refresher()
			self._song = self._loader()
		# self._root.update()
		self._shuffle["state"] = "normal"

	def _updating(self):
		mins, secs = divmod(self.duration, 60)
		self.total_length = f"{round(mins):02}:{round(secs):02}"

		if len(self._stored) == 10:
			self._stored.delete_last()
			self._stored.insert_first(self._song)
		elif len(self._stored) < 10:
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
		if self.time_cnt is not None:
			self._root.after_cancel(self.time_cnt)
		self._progress_variable.set(0)
		self.time_cnt = None
		self._start = 0
		self._root.update()
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
		
		self._set_uptime(self._start)
		self._root.update()
		self._previous_btn["state"] = "normal"
		self._next_btn["state"] = "normal"


	def _onoff_repeat(self):
		if self._active_repeat:
			self._repeat_image = PhotoImage(file=os.path.join(BASE_DIR, "shuffle_RGB.png"))
			self._repeat_btn["image"] = self._repeat_image
		else:
			self._repeat_image = PhotoImage(file=os.path.join(BASE_DIR, "repeat_RGB.png"))
			self._repeat_btn["image"] = self._repeat_image
		self._active_repeat = not self._active_repeat
		

	def _update_speakers(self, photo):
		# from PIL import Image
		# i = Image.open("sb.png")
		# i.thumbnail((40,40), Image.ANTIALIAS)
		# i.save("sb_RGB.png")
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
			mixer.quit()
			self._root.destroy()
			sys.exit()

	def _info(self, s):
		"""Returns tuple(freq,duration,mode,title)"""
		songdetails = MP3(s)
		return songdetails.info.sample_rate, songdetails.info.length, songdetails.info.mode

	def _convert(self, text):
		# print(len(text))
		elem = [i if ord(i) < 65535 else "." for i in text]
		if len(elem) > 49:
			elem = elem[:49] + ["..."]

		return "".join(elem)

	def _update_labels(self,song,dur):
		if self._title_txt == "MUSIC PAUSED" or len(self._title_txt) <= 54:
			self._title_txt_anchor = CENTER
			self._title["anchor"] = self._title_txt_anchor
		elif len(self._title_txt) > 54:
			self._title_txt_anchor = W
			self._title["anchor"] = self._title_txt_anchor
		self._title["text"] = self._convert(song)
		self._duration_label["text"] = dur

	def _about(self):
		"""Shows information about the player"""
		showinfo("Lazy Selector",
				"Lazy Selector\nVersion: 3.0\n\n      An audio player that reads MP3 files only"+\
				"\nThe previous button goes back 10 previous songs\n\nDeveloped by Ernesto")

	def _update_color(self, bg, fg, img):
		Player.BG = bg
		Player.FG = fg
		Player.MN = bg
		Player._CONFIG.set("theme","bg",Player.BG)
		Player._CONFIG.set("theme","fg",Player.FG)
		Player._CONFIG.set("theme","photo",img)
		self._update_theme()
		self._update_speakers(img)
		self._update_labels(self._title_txt,self.total_length)

	def _stop_play(self):
		self._play_btn["state"] = "disabled"
		self._play_btn_text = "PLAY"
		self._play_btn_command = self._unpause
		self._root.after_cancel(self.time_cnt)
		self.time_cnt = None
		if self.time_cnt is not None:
			# print(self.time_cnt)
			self._root.after_cancel(self.time_cnt)
		mixer.music.pause()
		self._title["anchor"] = CENTER
		self._title_txt = "MUSIC PAUSED"
		self._title["text"] = self._title_txt
		self._play_btn["text"] = self._play_btn_text
		self._play_btn["command"] = self._play_btn_command
		self._root.update()
		self._paused = True
		self._play_btn["state"] = "normal"

	def _unpause(self):
		"""Resumes playback"""
		self._play_btn["state"] = "disabled"
		self._paused = False
		self._play_btn_command = self._stop_play
		self._play_btn_text = "PAUSE"
		self._title["anchor"] = self._title_txt_anchor
		self._title_txt = os.path.splitext(os.path.basename(self._song))[0]
		self._title["text"] = self._convert(self._title_txt)
		self._play_btn["text"] = self._play_btn_text
		self._play_btn["command"] = self._play_btn_command
		mixer.music.unpause()
		self._set_uptime(self._start)
		self._root.update()
		self._play_btn["state"] = "normal"

	# def _playback(self):
	# 	pos = self._progress_variable.get()
	# 	mixer.music.play(start=int(pos))
	# 	self._set_uptime(pos)

	def _slide(self, value):
		if mixer.music.get_busy():
			if self.time_cnt is not None:
				self._root.after_cancel(self.time_cnt)
			self._progress_variable.set(value)
			pos = self._progress_variable.get()
			mixer.music.load(self._song)
			mixer.music.play(start=int(pos))
			self._set_uptime(pos)
		else:
			self._progress_variable.set(value)

	def _set_uptime(self, playtime):

		"""Updates current time"""
		
		self._start = playtime  # (int(mixer.music.get_pos()/1000))
		mins, secs = divmod(self._start, 60)
		self._time = f"{round(mins):02}:{round(secs):02}"
		self._current_time.config(text=self._time)
		self._progress_variable.set(self._start)
		self._start +=1
		self.time_cnt = self._root.after(1000, lambda:self._set_uptime(self._start))

		if not mixer.music.get_busy():
			#self._root.after_cancel(self.time_cnt)
			self._takeover()
		if self._paused:
			# print(self._paused)
			return
		# if self._start > round(self.duration):
		# 	self._root.after_cancel(self.time_cnt)
		# print(self._progress_variable.get())
	
if __name__ == '__main__':
	
	tk = Tk()
	tk.style = ThemedStyle()
	# ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
	tk.style.theme_use("arc")
	p = Player(tk)
	tk.mainloop() 