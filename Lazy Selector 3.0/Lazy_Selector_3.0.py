
from threading import Thread
from tkinter import Tk, Label, Button, Canvas, PhotoImage, W, Menu, CENTER, DoubleVar
# import ctypes
# co_initialize = ctypes.windll.ole32.CoInitialize
from tkinter.filedialog import askopenfilenames
from tkinter.ttk import Scale
from ttkthemes import ThemedStyle
# Force STA thread mode for tkinter's askdirectory()
# co_initialize(None)
from pyglet.media import Player as p_mixer
from pyglet.media import load as p_load
from pyglet.lib import load_library
import pyglet
import os
from plyer import battery, notification, filechooser
import sys
from subprocess import check_output
from random import shuffle
from deque import Deque
from time import sleep
from datetime import timedelta
from tkinter.messagebox import askokcancel, showinfo
from configparser import ConfigParser


def process_exists(process_name):
    call = "tasklist", "/FI", "imagename eq %s" % process_name
    output = check_output(call).decode()
    # check last line for process name
    last_line = output.strip().split("\r\n")[-1]
    return last_line.lower().startswith(process_name.lower())


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def r_path(relpath):
    """Get absolute path"""
    base_path = getattr(sys, "_MEIPASS", BASE_DIR)
    return os.path.join(base_path, relpath)


DATA_DIR = r_path("data")


class Player:
    """Plays mp3 audio files in shuffle mode
    win is tkinter's toplevel widget Tk"""
    _CONFIG = ConfigParser()
    _CONFIG.read(DATA_DIR + "\\lazylog.ini")
    BG = _CONFIG["theme"]["bg"]
    FG = _CONFIG["theme"]["fg"]
    MN = BG

    def __init__(self, win):
        #load_library("avbin")
        pyglet.have_avbin = True
        self._root = win
        self._root.geometry("318x116+" + Player._CONFIG["window"]["position"])
        # self._root.resizable(0, 0)
        # self._root.config(bg=Player.MN)
        self._root.title("")
        self._root.iconbitmap(default=DATA_DIR + "\\musicapp.ico")
        self._root.tk_focusFollowsMouse()
        self._root.wm_protocol("WM_DELETE_WINDOW", self._kill)
        # self.back_image = PhotoImage(file = )

        self.shuffle_mixer = p_mixer()
        self._progress_variable = DoubleVar()
        self._loaded_files = []
        self._all_files = []
        self.num = 0
        self.played = False
        self.previewed = False
        self._play_btn_text = ""
        self._title_txt = ""
        self._repeat_image = PhotoImage(
            file=os.path.join(DATA_DIR, "shuffle_RGB.png"))
        self.back_image = PhotoImage(
            file=os.path.join(DATA_DIR, "darkshuffle.png"))
        self._play_btn_command = None
        self._play_prev_command = None
        self._play_next_command = None
        self._active_repeat = False
        self._files_selected = False
        self._slider_above = False
        self._stored = Deque()
        self._playing = False
        self._open_folder = False

        self.menubar = Menu(self._root)
        self._root.config(menu=self.menubar)
        self.file_menu = Menu(self.menubar, tearoff=0,
                              fg=Player.FG, bg=Player.BG)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(
            label="Open Folder", command=self._manual_add)
        # self.file_menu.add_command(
        #     label="Add To Queue", command=self._select_fav)

        self.theme_menu = Menu(self.menubar, tearoff=0,
                               fg=Player.FG, bg=Player.BG)
        self.menubar.add_cascade(label="Themes", menu=self.theme_menu)
        self.theme_menu.add_command(label="White", command=lambda: self._update_color(
            "white smoke", "black", "gray_RGB.png"))
        self.theme_menu.add_command(label="Pink", command=lambda: self._update_color(
            "DeepPink3", "white", "bw_RGB.png"))

        self.about_menu = Menu(self.menubar, tearoff=0,
                               fg=Player.FG, bg=Player.BG)
        self.menubar.add_cascade(label="Help", menu=self.about_menu)
        self.about_menu.add_command(label="About", command=self._about)
        self.about_menu.add_command(
            label="Switch Slider", command=self._change_place)
        self._init()
        self._root.lift()
        self._refresher()
        self._set_thread(self._set_uptime, "Timer").start()

        if battery.get_state()["percentage"] < 70:
            notification.notify(title="Lazy Selector",
                                message=f'{battery.get_state()["percentage"]}% Charge Available.',
                                app_name="Lazy Selector",
                                timeout=5,
                                app_icon=DATA_DIR + "\\musicapp.ico")

    def _init(self):

        self.b = Canvas(self._root, width=310, height=110)
        self.b.place(x=2, y=0)
        self.b.create_image(0, 0, image=self.back_image, anchor="nw")
        self.progress_bar = Scale(self._root, from_=0, orient="horizontal", length=305,
                                  cursor="hand2", variable=self._progress_variable, command=self._slide)
        self.progress_bar.style = ThemedStyle()
        self.progress_bar.style.theme_use("equilux")
        self.progress_bar.place(x=4, y=92)

        self.current_time = Label(self.b, padx=0, text="00:00",
                                  bg=Player.BG, font=('arial', 9, 'bold'), fg=Player.FG, width=6, anchor="e")
        self.current_time.place(x=41, y=68)

        self._title = Label(self.b, pady=0, bg=Player.BG, text=self._title_txt,
                            font=('arial', 8, 'bold'), fg=Player.FG, width=44)
        self._title.place(x=1, y=1)

        # self._duration_label = Label(self.b, padx=0, text="00:00",
        #                              bg=Player.BG, font=("arial", 9, "bold"), fg=Player.FG, width=5)
        # self._duration_label.place(x=227, y=68)
        self._shuffle = Button(self.b, command=self.on_eos, text="SHUFFLE", padx=10, relief="flat",
                               bg=Player.BG, fg=Player.FG, font=("arial", 15, "bold"))
        self._shuffle.place(x=91, y=20)

        self._previous_btn = Button(self.b, padx=5, bg=Player.BG, fg=Player.FG, command=self._play_prev_command,
                                    font=("arial", 7, "bold"), width=5, height=1, text="I<<", relief="flat")
        self._previous_btn.place(x=90, y=68)

        self._play_btn = Button(self.b, padx=5, bg=Player.BG, text=self._play_btn_text, command=self._play_btn_command,
                                fg=Player.FG, font=("arial", 7, "bold"), width=5, height=1, relief="flat")

        self._play_btn.place(x=140, y=68)

        self._next_btn = Button(self.b, padx=5, bg=Player.BG, text=">>I", command=self._play_next_command,
                                fg=Player.FG, font=("arial", 7, "bold"), width=5, height=1, relief="flat")

        self._next_btn.place(x=190, y=68)

        self._left_display = Label(
            self.b, height=37, width=40, bg=Player.BG)
        # self._left_display.place(x=41, y=20)

        self._right_display = Label(
            self.b, height=37, width=40, bg=Player.BG)
        # self._right_display.place(x=222, y=20)
        # self._update_speakers(Player._CONFIG["theme"]["photo"])

        self._repeat_btn = Button(self.b, pady=0, padx=0, bg=Player.BG, command=self._onoff_repeat, width=20, height=15,
                                  relief="flat", font=("arial", 6, "bold"), anchor=W, image=self._repeat_image)
        self._repeat_btn.place(x=240, y=67)

    def _change_place(self):

        if self._slider_above:
            self._pb = 92
            self._controls = 68
        else:
            self._pb = 68
            self._controls = 86
        self.progress_bar.place(x=2, y=self._pb)
        self.current_time.place(x=41, y=self._controls)
        # self._duration_label.place(x=227, y=self._controls)
        self._previous_btn.place(x=90, y=self._controls)
        self._play_btn.place(x=140, y=self._controls)
        self._next_btn.place(x=190, y=self._controls)
        self._repeat_btn.place(x=240, y=self._controls)
        self._root.update()
        self._slider_above = not self._slider_above

    def _update_theme(self):

        # self._root.config(bg=Player.MN)
        self._repeat_btn["bg"], self._repeat_btn["fg"] = Player.BG, Player.FG
        self._play_btn["bg"], self._play_btn["fg"] = Player.BG, Player.FG
        self._next_btn["bg"], self._next_btn["fg"] = Player.BG, Player.FG
        self._shuffle["bg"], self._shuffle["fg"] = Player.BG, Player.FG
        self._previous_btn["bg"], self._previous_btn["fg"] = Player.BG, Player.FG
        # self._duration_label["bg"], self._duration_label["fg"] = Player.BG, Player.FG
        self.current_time["bg"], self.current_time["fg"] = Player.BG, Player.FG
        self._title["bg"], self._title["fg"] = Player.BG, Player.FG
        self.file_menu["bg"], self.file_menu["fg"] = Player.BG, Player.FG
        self.theme_menu["bg"], self.theme_menu["fg"] = Player.BG, Player.FG
        self.about_menu["bg"], self.about_menu["fg"] = Player.BG, Player.FG

    def _manual_add(self):
        self._open_folder = True
        self._refresher()

    def _refresher(self):
        if len(PASSED_FILES) > 0:
            self._all_files = [i for i in PASSED_FILES]
            self._songspath = os.path.dirname(self._all_files[0])
            PASSED_FILES.clear()
            print("Songspath:", self._songspath)
        else:
            try:
                # try getting the previous folder
                file = Player._CONFIG["files"]["folder"]
                self._songspath = file
            except KeyError:
                try:
                    self._songspath = filechooser.choose_dir(
                        title="Choose a Folder with Media Files")[0]
                except IndexError:
                    self._songspath = ""
                # failed, set the folder opened
                Player._CONFIG.set("files", "folder", self._songspath)
                file = self._songspath  # get the folder
            if self._open_folder and len(PASSED_FILES) == 0:
                try:
                    self._songspath = filechooser.choose_dir(
                        title="Choose a Folder with Media Files")[0]
                except IndexError:
                    self._songspath = ""
            self._root.title("LOADING...")

            if (file == self._songspath) and (self._all_files != []):
                # don't update the songs list
                pass
            else:
                # update
                try:
                    self._all_files = os.listdir(self._songspath)

                except FileNotFoundError:
                    # if log file isn't empty and songs list is empty
                    if (file != "") and (self._all_files == []):
                        self._songspath = file
                        self._all_files = os.listdir(self._songspath)
                    # if no directory was chosen and songs list isn't empty
                    elif (self._songspath == "") and (self._all_files != []):
                        self._songspath = file
                    else:
                        if askokcancel("Lazy Selector",
                                       "First time requires that you select a folder!\n    Do you want to select a folder again?"):
                            self._open_folder = True
                            self._refresher()
                        else:
                            sys.exit()
                            self._root.destroy()
                shuffle(self._all_files)
                self._root.title(
                    f"Lazy Selector - {os.path.basename(self._songspath)}".ljust(24))
        Player._CONFIG.set("files", "folder", self._songspath)
        self._open_folder = False

    def _loader(self):
        for i in self._all_files:
            # self.randnum = random.randint(0, len(self._all_files)-1)
            # self._extract = self._all_files[int(self.randnum)]
            if i.endswith('.mp3') or i.endswith('.m4a') or i.endswith(".aac"):
                filepath = os.path.join(self._songspath, i)
            else:
                self._all_files.remove(i)
                continue
            self._all_files.remove(i)
            self.num = 1
            try:
                yield filepath
            except Exception as e:
                str_error = str(e).split()
                if ("'song'" in str_error) and (self.num == 0):
                    yield "mp3"
                else:
                    yield False

    def _select_fav(self):

        loaded_files = askopenfilenames(filetypes=[("MP3 files", "*.mp3")])
        if len(loaded_files) != 0 and len(self._loaded_files) == 0:
            self._files_selected = True
            self._loaded_files = [i for i in loaded_files]

        else:
            self._files_selected = True
            for a in loaded_files:
                self._loaded_files.append(a)

        for audio in self._loaded_files:
            song = os.path.basename(audio)
            if song in self._all_files:
                self._all_files.remove(song)

    def _load_files(self):
        for i in self._loaded_files:
            song = self._loaded_files[i]
            self._loaded_files.remove(song)
            yield song

    def _mixer(self, load):
        source = p_load(load)
        self.shuffle_mixer.queue(source)
        # In the middle of playing
        if self.shuffle_mixer.playing or (self.shuffle_mixer.source and self.played) or self.previewed:
            self.shuffle_mixer.next_source()
        return self.shuffle_mixer

    def on_eos(self):
        # if self._playing:
        self._playing = False
        self._start = 0
        # self._shuffle["state"] = "disabled"
        self._play_btn_text = "PAUSE"
        self._play_btn["text"] = self._play_btn_text
        self._play_prev_command = lambda: self._play_prev()
        self._play_btn_command = self._stop_play

        if not self._files_selected:

            try:
                self._song = next(self._loader())
                try:
                    self._mixer(self._song).play()
                except ValueError:
                    print("ValueError")
                    self._song = next(self._loader())
                    self._mixer(self._song).play()

                self._previous_btn["command"] = self._play_prev_command
                self._play_btn["command"] = self._play_btn_command
                self._set_thread(self._run_event, "Pyglet Event").start()
                self.duration = round(self.shuffle_mixer.source.duration)
            except StopIteration:
                self._song = False
        self._updating()

        # elif self._files_selected:
        #     try:
        #         self.seg = self._next_files.pop()
        #     except IndexError:
        #         pass
        # if len(self._loaded_files) == 0:
        #     self._files_selected = False

        if self._song == "mp3":
            self._open_folder = True
            try:
                showinfo(
                    "Lazy Selector", f"{os.path.basename(self._songspath)} folder has no MP3 files.\n\n   Choose a different Folder.")
            except AttributeError:
                showinfo("Lazy Selector", "No folder initialized!")
            self._refresher()
            # self._song = next(self._loader())

        elif not self._song and len(PASSED_FILES) == 0 and len(self._all_files) == 0:
            print(len(PASSED_FILES), len(self._all_files))
            self._open_folder = True
            showinfo("Lazy Selector",
                     "                              Done Playing."
                     "\n\nClick Cancel in the next dialog to repeat the just ended folder.")
            self._refresher()
            # self._song = next(self._loader())

        self._playing = True
        # self.played = True
        self._shuffle["state"] = "normal"

    def _updating(self):

        # if self.shuffle_mixer.source is not None:
        self._title_txt = os.path.splitext(os.path.basename(self._song))[0]
        self.progress_bar["to"] = round(int(self.duration))

        if len(self._stored) == 7:
            self._stored.delete_last()
            self._stored.insert_first(self._song)
        elif len(self._stored) < 7:
            self._stored.insert_first(self._song)

        self._update_labels(self._title_txt)
        self._prev_song = self._stored.first()

    def _play_prev(self, prev=True):

        self._play_btn_text = "PAUSE"
        self._playing = False
        self.previewed = True
        self._start = 0
        self._play_btn_command = self._stop_play
        self._play_next_command = lambda: self._play_prev(prev=False)
        self._next_btn["command"] = self._play_next_command
        if prev:
            self._previous_btn["state"] = "disabled"
            try:
                if self._prev_song.next_.element_ is not None:
                    self._song = self._prev_song.next_.element_
                    self._prev_song = self._prev_song.next_
            except Exception as e:
                print(e)
                pass
        else:
            self._next_btn["state"] = "disabled"
            try:
                if self._prev_song.prev.element_ is not None:
                    self._song = self._prev_song.prev.element_
                    self._prev_song = self._prev_song.prev
            except Exception as e:
                print(e)
                pass

        self._play_btn["text"] = self._play_btn_text
        self._play_btn["command"] = self._play_btn_command
        self._previous_btn["state"] = "normal"
        self._next_btn["state"] = "normal"
        self._mixer(self._song).play()
        # Check duration after queue
        self._title_txt = os.path.splitext(os.path.basename(self._song))[0]
        self._update_labels(self._title_txt)
        self.duration = round(self.shuffle_mixer.source.duration)
        self.progress_bar["to"] = round(int(self.duration))
        self.previewed = False
        self._playing = True

    def _onoff_repeat(self):
        if self._active_repeat:
            self._repeat_image = PhotoImage(
                file=os.path.join(DATA_DIR, "shuffle_RGB.png"))
            self._repeat_btn["image"] = self._repeat_image
        else:
            self._repeat_image = PhotoImage(
                file=os.path.join(DATA_DIR, "repeat_RGB.png"))
            self._repeat_btn["image"] = self._repeat_image
        self._active_repeat = not self._active_repeat
        self.shuffle_mixer.loop = self._active_repeat

    def _update_speakers(self, photo):
        # from PIL import Image
        # i = Image.open("blue.jpeg")
        # i.thumbnail((324, 116), Image.ANTIALIAS)
        # i.save("blue_RGB.jpeg")
        self.speaker = PhotoImage(file=os.path.join(DATA_DIR, photo))
        self._left_display.config(image=self.speaker, bg=Player.BG)
        self._right_display.config(image=self.speaker, bg=Player.BG)

    def _run_event(self):

        from pyglet.app import run
        try:
            run()
        except Exception:  # RuntimeError, ReferenceError
            pass

    def _kill(self):

        if self._playing:
            if askokcancel("Lazy Selector", "Music is still playing.\n      Quit Anyway?"):
                try:
                    Player._CONFIG.set(
                        "window", "position", f"{self._root.winfo_x()}+{self._root.winfo_y()}")
                    with open(DATA_DIR + "\\lazylog.ini", "w") as f:
                        Player._CONFIG.write(f)
                except Exception as er:
                    pass
                self.shuffle_mixer.delete()
                self._root.destroy()
                sys.exit()
        else:
            try:
                with open(DATA_DIR + "\\lazylog.ini", "w") as f:
                    Player._CONFIG.write(f)
            except Exception as er:
                pass
            self.shuffle_mixer.delete()
            self._root.destroy()
            sys.exit()

    def _convert(self, text):
        # print(len(text))
        elem = [i if ord(i) < 65535 else "." for i in text]
        if len(elem) > 53:
            elem = elem[:51] + ["..."]

        return "".join(elem)

    def _update_labels(self, song):
        if self._title_txt == "MUSIC PAUSED" or len(self._title_txt) <= 49:
            self._title_txt_anchor = CENTER
            self._title["anchor"] = self._title_txt_anchor
        elif len(self._title_txt) >= 50:
            self._title_txt_anchor = W
            self._title["anchor"] = self._title_txt_anchor
        self._title["text"] = self._convert(song)
        # self._duration_label["text"] = dur

    def _about(self):
        """Shows information about the player"""
        showinfo("Lazy Selector",
                 "Lazy Selector\nVersion: 3.0\n\n      An audio player that reads MP3 files only"
                 "\nThe previous button goes back 2 previous songs\n\nDeveloped by Ernesto")

    def _update_color(self, bg, fg, img):
        Player.BG = bg
        Player.FG = fg
        Player.MN = bg
        Player._CONFIG.set("theme", "bg", Player.BG)
        Player._CONFIG.set("theme", "fg", Player.FG)
        Player._CONFIG.set("theme", "photo", img)
        self._update_theme()
        # self._update_speakers(img)
        self._update_labels(self._title_txt)

    def _stop_play(self):
        self._play_btn["state"] = "disabled"
        self._play_btn_text = "PLAY"
        self._play_btn_command = self._unpause
        self._playing = False
        self._title["anchor"] = CENTER
        self._title_txt = "MUSIC PAUSED"
        self._title["text"] = self._title_txt
        self._play_btn["text"] = self._play_btn_text
        self._play_btn["command"] = self._play_btn_command
        self._play_btn["state"] = "normal"
        self.shuffle_mixer.pause()

    def _unpause(self):
        """Resumes playback"""
        self._play_btn["state"] = "disabled"
        self._play_btn_command = self._stop_play
        self._play_btn_text = "PAUSE"
        self._title["anchor"] = self._title_txt_anchor
        self._title_txt = os.path.splitext(os.path.basename(self._song))[0]
        self._title["text"] = self._convert(self._title_txt)
        self._play_btn["text"] = self._play_btn_text
        self._play_btn["command"] = self._play_btn_command
        # self._root.update()
        self._play_btn["state"] = "normal"
        self.shuffle_mixer.play()
        self._playing = True

    def _set_thread(self, func, nm, c=()):
        return Thread(target=func, args=c, daemon=True, name=nm)

    def _slide(self, value):
        if self._playing:
            self._playing = False
            self._progress_variable.set(round(float(value)))
            pos = self._progress_variable.get()
            sleep(0.2)
            self._start = pos
            self.shuffle_mixer.seek(round(float(value)))
            self._playing = True
        else:
            self._progress_variable.set(value)

    def _set_uptime(self):
        """Updates current time"""

        said = False
        while True:
            if self._playing:
                if self._start >= 3600:
                    ftime = timedelta(seconds=round(self._start))
                else:
                    mins, secs = divmod(self._start, 60)
                    ftime = f"{round(mins):02}:{round(secs):02}"

                self.current_time.config(text=ftime)
                self._progress_variable.set(self._start)
                sleep(1)
                self._start += 1
                if battery.get_state()["percentage"] < 70 and not said:
                    notification.notify(title="Lazy Selector",
                                        message=f'{battery.get_state()["percentage"]}% Charge Available.',
                                        app_name="Lazy Selector",
                                        timeout=20,
                                        app_icon=DATA_DIR + "\\musicapp.ico")
                    said = True
                if self.shuffle_mixer._audio_player is None and not self._active_repeat:
                    print("Finished in:", self._start)
                    self.on_eos()
                elif self.shuffle_mixer.time <= 1 and self._active_repeat:
                    self._start = 0

            else:
                sleep(0.4)
                continue


if not process_exists("Lazy_Selector_3.0.exe"):

    PASSED_FILES = sys.argv[1:]
    print(len(PASSED_FILES), PASSED_FILES)
    tk = Tk()
    # tk.style = Style()
    # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
    # tk.style.theme_use("clam")
    p = Player(tk)
    tk.mainloop()
