

from tkinter import Tk, Label, Frame, Button, GROOVE, Canvas, PhotoImage, W, Menu, CENTER, SE, FLAT
from tkinter.ttk import Style
import random, os
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from deque import Deque
from tkinter.messagebox import askokcancel, showinfo
from tkinter.filedialog import askdirectory
from pygame import mixer, init


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Player:
	"""Plays mp3 audio files in shuffle mode
	win is tkinter's toplevel widget Tk"""
	BG = "gray12"
	FG = "gray91"
	MN = "gray12"
	def __init__(self, win):
		init()
		self._root = win
		self.total_length = ""
		self._song = ""
		self._all_files = []
		self.num = 0
		self._prev_f = 44100
		self._time = ""
		self._text = ""
		self._title_txt = ""
		self._repeat_txt = "Repeat Off"
		self._start = 0
		self._command = None
		self._repeat_com = self._enable_repeat
		self._active_repeat = False
		self._stored = Deque()
		self.time_cnt = "after#0"
		self.cnt = "after#0"

		self.menubar = Menu(self._root) 
		self._root.config(menu=self.menubar)
		self._menu(self.menubar,"File","Open Folder",com=self._refresher)

		self._menu(self.menubar,"Themes","Green",com=self._update_green)
		self.submenu.add_command(label="Pink",command=self._update_pink)
		self.submenu.add_command(label="Blue",command=self._update_blue)
		self.submenu.add_command(label="Brown",command=self._update_brown)
		self.submenu.add_command(label="Dark",command=self._update_dark)

		self._menu(self.menubar, "Help","About",com=self._about)
		self._init()
		self._refresher()

	def _init(self):
		self._root.title("Lazy Selector".ljust(34))
		self._root.geometry("310x81+1038+5")
		self._root.resizable(height=False, width=False)
		self._root.config(bg=Player.MN)
		self._root.iconbitmap(default=BASE_DIR+"\\musicapp.ico")
		self._root.tk_focusFollowsMouse()


		self._current_time = Label(self._root,padx=1,text=self._time,
									bg=Player.BG,font=('arial',7,'bold'),fg=Player.FG,width=5)
		self._current_time.place(x=1,y=1)
		self._title = Label(self._root, bg=Player.BG, anchor=W, text=self._title_txt,
							font=('arial',7,'bold'), fg=Player.FG, width=38)
		self._title.place(x=38, y=1)

		self._duration_label = Label(self._root, padx=1,
								bg=Player.BG,font=("arial",7,"bold"),fg=Player.FG,width=5)
		self._duration_label.place(x=273,y=1)

		self._shuffle = Button(self._root,command=self._play,text="SHUFFLE",padx=10,anchor=SE,
								bg=Player.BG,fg=Player.FG,font=("arial",15,"bold"))
		self._shuffle.place(x=1,y=19)
		
		self._previous_btn = Button(self._root,padx=5,bg=Player.BG,fg=Player.FG,font=("sans",7,"bold"),width=5,height=1,text="I<<")
		self._previous_btn.place(x=1,y=61)
		#self._pic_resize(BASE_DIR+"\\previous.png",46,13,self._previous_btn)


		self._play_btn = Button(self._root,padx=5,bg=Player.BG,text=self._text,command=self._command,
								fg=Player.FG,font=("arial",7,"bold"),width=5,height=1)
		
		self._play_btn.place(x=262,y=61)
		#self._pic_resize(BASE_DIR+"\\pause.png",45,13,self._play_btn)

		self._chooser = Button(self._root,command=self._refresher,padx=5,bg=Player.BG,
								fg=Player.FG,font=("arial",7,"bold"),width=33,height=1,text="=")
		#self._pic_resize(BASE_DIR+"\\pause.png",202,13,self._chooser)
		self._chooser.place(x=49,y=61)
		

		self._display = Canvas(self._root,width=175,height=36,relief=GROOVE,bg=Player.BG)
		self._display.place(x=129,y=19)

		# --> Frame
		self._topframe = Frame(self._root, bg=Player.BG, width=50, height=15)
		self._topframe.place(x=2,y=20)

		self._repeat_btn = Button(self._topframe,bg=Player.BG,width=8,command=self._repeat_com,relief=FLAT,
									fg=Player.FG,font=("sans",6,"bold"),text=self._repeat_txt,anchor=W)
		self._repeat_btn.place(x=0,y=0)



	def _refresher(self):
		self._songspath = askdirectory(title="Choose a Music Folder with MP3 Audio Files")
		with open(BASE_DIR+"\\lazylog.txt") as f:
			file = f.readline().strip("\n")
			if (file == self._songspath) and (self._all_files != []):
				#don't update the songs list
				pass
				f.close()

			else:
				#update
				try:
					self._all_files = os.listdir(self._songspath)
					with open(BASE_DIR+"\\lazylog.txt","w") as f:
						f.write(self._songspath)
				except FileNotFoundError:
					if (file != "") and (self._all_files == []): # if txt file isn't empty and songs list is empty
						self._songspath = file
						self._all_files = os.listdir(self._songspath)
					elif (self._songspath == "") and (self._all_files != []): # if no directory was chosen and songs list isn't empty
						self._songspath = file
					else:
						if askokcancel("Lazy Selector",
										"First time requires that you select a folder!\n    Do you want to select a folder again?"):
							self._refresher()
						else:
							self._root.destroy()
	
	def _loader(self):
		for i in range(len(self._all_files)):
			self.randnum = random.randint(0, len(self._all_files)-1)
			self._extract = self._all_files[int(self.randnum)]
			if self._extract.endswith('.mp3'):
				song = os.path.join(self._songspath, self._extract)
				try:       
					freq, duration, mode, title = self._info(song)
				except Exception as er:
					continue
			else:
				self._all_files.remove(self._extract)
				continue
			self._all_files.remove(self._extract)
			self.num +=1
			break
		try:
			return [self.randnum, song, duration, freq]
		except Exception as e:
			str_error = str(e).split()
			if ("'song'" in str_error) and (self.num == 0):
				return "mp3"
			else:
				return False
		

	def _play(self):
		self._start = 0
		self._text = "PAUSE"
		self._command = self._stop_play
		self._root.after_cancel(self.time_cnt)
		self._load = self._loader()
		if self._active_repeat:
			pass
		elif (self._load) and (self._load != "mp3") and (not self._active_repeat):
			self._song = self._load[1]
			self.duration = self._load[2]
			self._freq = self._load[3]

		if not self._load:
			self._root.after_cancel(self.cnt)
			showinfo("Lazy Selector",
					"     All folder songs have played. Select another folder to play"\
					"\nClick Cancel in the Folder chooser to repeat the just ended folder.")
			self._refresher()
			self._load = self._loader()
		elif self._load == "mp3":
			showinfo("Lazy Selector","The selected Folder has no MP3 files.\n      Choose a different Folder.")
			self._refresher()
			self._load = self._loader()
		else:
			try:
				self._mixer(self._song,self._freq)
				self._play_btn["text"] = self._text
				self._play_btn["command"] = self._command
			except Exception as e:
				pass
			mins, secs = divmod(self.duration, 60)
			self.total_length = f"{round(mins):02}:{round(secs):02}"
			after = int(round(self.duration)*1000)
			self._root.after_cancel(self.cnt)
			if mixer.music.get_busy() == 1:
				self.cnt = self._root.after(after, self._play)
			else:
				self.cnt = self._root.after(1,self._play)

			if len(self._stored) == 7 and not self._active_repeat:
				self._stored.delete_last()
				self._stored.insert_first(self._song)
			elif len(self._stored) < 7 and not self._active_repeat:
				self._stored.insert_first(self._song)
			self._title_txt = os.path.basename(self._song)
			self._update_labels(self._title_txt,self.total_length)
			self._previous_btn["command"] = self._play_prev
			self._set_uptime()
	
	def _play_prev(self):
		self._text = "PAUSE"
		self._command = self._stop_play
		self._root.after_cancel(self.cnt)
		self._root.after_cancel(self.time_cnt)
		self._start = 0
		try:
			self._song = self._stored.delete_first()
		except Exception as e:
			self._song = self._song
		self._freq, self.duration, mode, title = self._info(self._song)
		self._mixer(self._song, self._freq)
		self._title_txt = os.path.basename(self._song)
		mins, secs = divmod(self.duration, 60)
		self.total_length = f"{round(mins):02}:{round(secs):02}"
		self._update_labels(self._title_txt,self.total_length)
		self._play_btn["text"] = self._text
		self._play_btn["command"] = self._command
		self.cnt = self._root.after(round(self.duration)*1000,self._play)
		self._set_uptime()

	def _enable_repeat(self):
		self._repeat_txt = "Repeat On"
		self._repeat_com = self._disable_repeat
		self._repeat_btn["text"] = self._repeat_txt
		self._repeat_btn["command"] = self._repeat_com
		self._active_repeat = True

	def _disable_repeat(self):
		self._repeat_txt = "Repeat Off"
		self._repeat_com = self._enable_repeat
		self._repeat_btn["text"] = self._repeat_txt
		self._repeat_btn["command"] = self._repeat_com
		self._active_repeat = False

	def _mixer(self, s, f):
		if not self._prev_f == f:
			mixer.quit()
		mixer.pre_init(frequency=f,buffer=1024,allowedchanges=0)
		mixer.init()
		mixer.music.load(s)
		mixer.music.play()
		self._prev_f = f

	def _info(self, s):
		"""Returns tuple(freq,duration,mode,title)"""
		songdetails = MP3(s)
		tag = ID3(s)
		freq = songdetails.info.sample_rate
		duration = songdetails.info.length
		mode = songdetails.info.mode
		title = tag["TIT2"].text[0]
		return freq, duration, mode, title

	def _update_labels(self,song,dur):
		if self._title_txt == "MUSIC PAUSED":
			self._title["anchor"] = CENTER
		else:
			self._title["anchor"] = W
		self._title["text"] = song
		self._duration_label["text"] = dur

	def _menu(self,master,top,name,com=None):
		self.submenu = Menu(master,tearoff=0)
		self.menubar.add_cascade(label=top, menu=self.submenu)
		self.submenu.add_command(label=name,command=com)

	def _about(self):
		"""Shows information about the player"""
		showinfo("Lazy Selector",
				"Lazy Selector\nVersion: 2.0\n\n      An audio player that reads MP3 files only"+\
				"\nThe previous button goes back 7 previous songs\n\nDeveloped by Ernesto")

	def _update_green(self):
		Player.BG = "lime green"
		Player.FG = "black"
		self._init()
		self._update_labels(self._title_txt,self.total_length)
	def _update_brown(self):
		Player.BG = "brown4"
		Player.FG = "gray91"
		self._init()
		self._update_labels(self._title_txt,self.total_length)
	def _update_blue(self):
		Player.BG = "midnight blue"
		Player.FG = "gray91"
		self._init()
		self._update_labels(self._title_txt,self.total_length)
	def _update_pink(self):
		Player.BG = "DeepPink3"
		Player.FG = "gray91"
		self._init()
		self._update_labels(self._title_txt,self.total_length)
	def _update_dark(self):
		Player.BG = "gray12"
		Player.FG = "gray91"
		self._init()
		self._update_labels(self._title_txt,self.total_length)

	def _stop_play(self,event=None):
		self._text = "PLAY"
		self._title_txt = "MUSIC PAUSED"
		self._command = self._unpause
		self._root.after_cancel(self.time_cnt)
		self._root.after_cancel(self.cnt)
		mixer.music.pause()
		self._title["anchor"] = CENTER
		self._title["text"] = self._title_txt
		self._play_btn["text"] = self._text
		self._play_btn["command"] = self._command

	def _unpause(self,event=None):
		"""Resumes playback"""
		self._title_txt = os.path.basename(self._song)
		self._command = self._stop_play
		self._text = "PAUSE"
		self._title["anchor"] = W
		self._title["text"] = self._title_txt
		self._play_btn["text"] = self._text
		self._play_btn["command"] = self._command
		mixer.music.unpause()
		self.cnt = self._root.after(((int(self.duration)-int(self._start))*1000),self._play)
		self._set_uptime()

	def _set_uptime(self):
		"""Updates current time"""
		
		mins, secs = divmod(self._start, 60)
		self._time = f"{round(mins):02}:{round(secs):02}"
		self._current_time["text"] = self._time
		self._start += 1
		self.time_cnt = self._root.after(1000,self._set_uptime)


	"""def _pic_resize(self, file, width, height,widget):
		
		imgload = imread(file)
		img_object = cvtColor(imgload, COLOR_BGR2RGBA)
		img = Image.fromarray(img_object)
		img = img.resize((width,height))
		self.imgtk = ImageTk.PhotoImage(image=img)
		widget.config(width=width, height=height, image=self.imgtk)
		"""

		


tk = Tk()
p = Player(tk)
tk.mainloop() 
