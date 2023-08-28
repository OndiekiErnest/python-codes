__author__ = "Ernesto: ernestondieki12@gmail.com"
__version__ = "4.0"


from pyglet.media import Player as p_mixer
from pyglet.media import load as p_load
from threading import Thread
from os import chmod, getpid, listdir, kill
from os.path import expanduser, join, dirname, basename, abspath, splitext, exists, isfile
from re import split as SPLIT
from base64 import b64decode
from subprocess import check_output
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
from plyer import battery, notification
from sys import exit
import sys
from random import shuffle
from images import *
from time import sleep
from datetime import timedelta
from tkinter import Tk, Frame, Label, Button, PhotoImage, Menu, DoubleVar, Listbox, Entry, Scrollbar, Toplevel, Canvas
from tkinter.ttk import Scale
from ttkthemes import ThemedStyle
try:
    from idlelib.tooltip import ToolTip
except ImportError:
    from idlelib.tooltip import Hovertip as ToolTip
from tkinter.messagebox import askokcancel, showinfo
from tkinter.filedialog import askopenfilenames, askdirectory
from configparser import ConfigParser

#TODO
def process_exists(process_name):
    # True or False

    call = "tasklist", "/FI", "imagename eq %s" % process_name
    output = check_output(call).decode()
    # check last line for process name
    last_line = output.strip().split("\r\n")[-1]
    # return last_line.lower().startswith(process_name.lower())
    try:
        return int(last_line.split()[1])
    except Exception: # TypeError
        return False
# print(repeat_img)
# print(b64decode(repeat_img))
BASE_DIR = dirname(abspath(__file__))


def r_path(relpath):
    """
        Get absolute path
    """

    base_path = getattr(sys, "_MEIPASS", BASE_DIR)
    return join(base_path, relpath)


DATA_DIR = r_path("data")
debug = False


class Player:
    """
        Plays mp3, m4a, aac audio files in shuffle and repeat mode
        win is tkinter's toplevel widget Tk
    """

    _CONFIG = ConfigParser()
    _CONFIG.read(DATA_DIR + "\\lazylog.cfg")
    try:
        BG = _CONFIG["theme"]["bg"]
        FG = _CONFIG["theme"]["fg"]
    except KeyError:
        BG = "gray97"
        FG = "black"
        try:
            _CONFIG.add_section("theme")
        except Exception:
            pass
        _CONFIG.set("theme", "bg", "gray97")
        _CONFIG.set("theme", "fg", "black")

    def __init__(self, win):
        self._root = win
        self._root.resizable(0, 0)
        self._root.config(bg=Player.BG)
        self._root.title("Lazy Selector")
        self._root.tk_focusFollowsMouse()
        self._root.wm_protocol("WM_DELETE_WINDOW", self._kill)
        self._root.wm_iconphoto(True, PhotoImage(data=APP_IMG))
        self._screen_height = self._root.winfo_screenheight() - 92
        if debug: print(self._screen_height)
        self.shuffle_mixer = p_mixer()
        self._progress_variable = DoubleVar()
        self._loaded_files = []
        self._all_files = []
        self.collected = []
        self.index = -1
        self.collection_index = None
        self._start = 0
        self.duration = 60
        self._title_txt = ""
        self._title_txt_anchor = "w"
        self.ftime = "00:00"
        self._play_btn_command = None
        self._play_prev_command = None
        self._play_next_command = None
        self.listbox = None
        self.list_frame = None
        self.main_frame = None
        self.done_frame = None
        self.sort_frame = None
        self.top = None
        self._active_repeat = False
        self._files_selected = False
        self._slider_above = False
        self.__supported_extensions = ('.mp3','.m4a','.aac')
        self._playing = False
        self._open_folder = False
        self.previous_img = PhotoImage(data=PREVIOUS_IMG)
        self.play_img = PhotoImage(data=PLAY_IMG)
        self.pause_img = PhotoImage(data=PAUSE_IMG)
        self.next_img = PhotoImage(data=NEXT_IMG)
        self.play_btn_img = self.play_img
        if Player.BG == "gray97":
            self._repeat_image = PhotoImage(data=REPEAT_IMG)
        else:
            self._repeat_image = PhotoImage(data=DARKREPEAT_IMG)

        self.menubar = Menu(self._root)
        self._root.config(menu=self.menubar)
        self.file_menu = Menu(self.menubar, tearoff=0,
                              fg=Player.FG, bg=Player.BG)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(
            label="Open Folder", command=self._manual_add)
        self.file_menu.add_command(
            label="Add to Queue", command=self._select_fav)

        self.theme_menu = Menu(self.menubar, tearoff=0,
                               fg=Player.FG, bg=Player.BG)
        self.menubar.add_cascade(label="Theme", menu=self.theme_menu)
        self.theme_menu.add_command(label="Light", command=lambda: self._update_color(
            "gray97", "black"))
        self.theme_menu.add_command(label="Dark", command=lambda: self._update_color(
            "gray28", "gray97"))

        self.about_menu = Menu(self.menubar, tearoff=0,
                               fg=Player.FG, bg=Player.BG)
        self.menubar.add_cascade(label="Help", menu=self.about_menu)
        self.about_menu.add_command(label="Switch Slider", command=self._change_place)
        self.about_menu.add_separator()
        self.about_menu.add_command(label="About Lazy Selector", command=self._about)
        self._set_thread(self._set_uptime, "Timer").start()
        self._init()
        self._refresher()

        if battery.get_state()["percentage"] < 51:
            notification.notify(title="Lazy Selector",
                                message=f'{battery.get_state()["percentage"]}% Charge Available',
                                app_name="Lazy Selector",
                                timeout=5,
                                app_icon=DATA_DIR + "\\app.ico")

#------------------------------------------------------------------------------------------------------------------------------

    def _on_enter(self, event):
        """
            On mouse over widget
        """

        event.widget["bg"] = "gray97"

    def _on_leave(self, event):
        """
            On mouse leave widget
        """

        if self.list_frame is not None:
            event.widget["bg"] = "gray28"
        else:
            event.widget["bg"] = Player.BG

#------------------------------------------------------------------------------------------------------------------------------

    def _update_bindings(self):
        """
            Mouse hover bindings
        """

        if self.list_frame is not None or Player.BG == "gray28":
            self._previous_btn.bind("<Enter>", self._on_enter)
            self._previous_btn.bind("<Leave>", self._on_leave)
            self._play_btn.bind("<Enter>", self._on_enter)
            self._play_btn.bind("<Leave>", self._on_leave)
            self._next_btn.bind("<Enter>", self._on_enter)
            self._next_btn.bind("<Leave>", self._on_leave)

#------------------------------------------------------------------------------------------------------------------------------

    def __update_listbox(self):
        """
            Inserts items to the Listbox
        """

        self.listbox.pack_forget()
        self.scrollbar.pack_forget()
        self.searchlabel["text"] = "Updating..."
        self.searchlabel.place(x=110, y=72)
        self.collection_index = None
        self.searchbar.delete(0, "end")
        self.listbox.delete(0, "end")
        try:
            self._root.geometry("318x116+" + f"{self._root.winfo_x()}+{self._root.winfo_y()}")
            for file in self._all_files:

                try:
                    self.listbox.insert("end", self._convert(file))
                except Exception:
                    continue
            self._resize_listbox()
            self.listbox.selection_set(self.index)
            self.listbox.see(self.index)
            self.searchlabel["text"] = "Search:"
            self.listbox.pack(side="left", padx=3)
            self.scrollbar.pack(side="left", fill="y")
        except AttributeError:
            pass

    def _update_listbox(self):
        """
            Threads __update_listbox function
        """

        if self.listbox is not None and self.scrollbar is not None:
            self._set_thread(self.__update_listbox, "Update Listbox").start()

#------------------------------------------------------------------------------------------------------------------------------

    def _resize_listbox(self):
        """
            Dynamically resize Listbox according to the number of items
        """

        self.searchlabel.place(x=130, y=72)
        self.searchbar.place(x=178, y=73)
        if self.listbox.size() > 37:
            self._root.geometry(f"318x{self._screen_height}+" + f"{self._root.winfo_x()}+{20}")
        else:
            height = 116 + (self.listbox.size() * 16)
            y = self._root.winfo_y()
            if debug: print("Listbox Height:", height, "Items:", self.listbox.size())
            difference = self._screen_height - (y+height)
            # if the new height surpasses screen height, then subtract the difference from y
            if difference < 0:
                y = y - (difference * -1)
            self._root.geometry(f"318x{height}+" + f"{self._root.winfo_x()}+{y}")

#------------------------------------------------------------------------------------------------------------------------------

    def __on_search(self):
        """
            Returns match for string searched else updates listbox
        """

        searchstr = self.searchbar.get()
        self.collected = []
        self.listbox.delete(0, "end")
        if debug: print("Searched:", searchstr)
        if searchstr != "":
            for song in self._all_files:
                if searchstr.lower() in song.lower():
                    try:
                        self.listbox.insert("end", self._convert(song))
                    except Exception:
                        continue
                    for item in self.listbox.get(0, "end"):
                        if song.startswith(item.strip("...")) or song.endswith(item.strip("...")) or \
                                splitext(item)[0].strip("...") in song:
                            self.collected.append(song)
            self._resize_listbox()
        else:
            print(self.collection_index)
            self._update_listbox()

    def _on_search(self, event):
        """
            Threads __on_search function
        """

        self._set_thread(self.__on_search, "Search").start()

#------------------------------------------------------------------------------------------------------------------------------

    def _delete_listitem(self):
        """
            Listbox's Remove from List
        """

        if debug: print(len(self._all_files))
        for i in self.listbox.curselection()[::-1]:
            if len(self.collected) == 0:
                item = self._all_files[i]
            else:
                item = self.collected[i]
            try:
                self._all_files.remove(item)
            except ValueError:
                pass
            if item in self.collected: self.collected.remove(item)
            self.listbox.delete(i)
            if debug: print(i, item)
        self._resize_listbox()
        if debug: print(len(self._all_files))

#------------------------------------------------------------------------------------------------------------------------------

    def _addto_queue(self):
        """
            Listbox's Play Next
        """
        try:
            i = self.listbox.curselection()[-1]

            if i == 0:
                self.listbox.selection_set(0)
                if self.shuffle_mixer._audio_player is None and not self._playing:
                    self._on_click()
            else:
                if len(self.collected) == 0 and (i != self.index and i > self.index): # if adding from main list
                    self.listbox.delete(i)
                    item = self._all_files[i]
                    try:
                        self._all_files.remove(item) # remove and insert later
                    except ValueError:
                        pass
                    self.listbox.insert(self.index + 1, item)
                    self._all_files.insert(self.index + 1, item)
                    if self.shuffle_mixer._audio_player is None and not self._playing: # if player hasn't started
                        self.listbox.selection_set(0)
                        self._on_click()
                    self.listbox.selection_set(self.index)
                elif (len(self.collected) != 0) and (i != self.collection_index and i > self.collection_index):
                    if i != self.collection_index:
                        self.listbox.delete(i)
                        item = self.collected[i]
                        if self.collection_index is None: # if no song from the searched has played
                            if item in self.collected: self.collected.remove(item)
                            self.listbox.insert(0, item)
                            self.collected.insert(0, item)

                            if self.shuffle_mixer._audio_player is None and not self._playing:
                                self.listbox.selection_set(0)
                                self._on_click()
                        elif i > self.collection_index: # if song from searched list had played
                            if item in self.collected: self.collected.remove(item)
                            self.listbox.insert(self.collection_index + 1, item)
                            self.collected.insert(self.collection_index + 1, item)
                            self.listbox.selection_set(self.collection_index)
                    if debug: print(self.collection_index)
        except IndexError: # IndexError
            pass

#------------------------------------------------------------------------------------------------------------------------------

    def _listbox_rightclick(self, event):
        """
            Popup event function to bind to right click
        """

        popup = Menu(self.listbox, tearoff=False, bg="gray28", fg="gray97", font=("New Times Roman", 9, "bold"),
                    activebackground="DeepSkyBlue3")
        popup.add_command(label="Play", command=self._on_click)
        popup.add_command(label="Play Next", command=self._addto_queue)
        popup.add_separator()
        popup.add_command(label="Remove from List", command=self._delete_listitem)
        try:
            popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            popup.grab_release()

#------------------------------------------------------------------------------------------------------------------------------

    def scroll_widget(self, event):
        """
            Event function to bind to mouse wheel
        """

        event.widget.yview_scroll(int(-1 * (event.delta / 120)), "units")

#------------------------------------------------------------------------------------------------------------------------------

    def _tips(self):
        """
            On mouse over
        """

        if self.main_frame is not None and Player.BG == "gray97":
            ToolTip(self._previous_btn, "Previous")
            ToolTip(self._play_btn, "Pause/Play")
            ToolTip(self._next_btn, "Next")

#----------------------------------------------------------------------------------------------------------------------

    def _init(self):
        """
            Main window
            Called from self.list_frame or from self.sort_frame
            or after self.done_frame is set to None
        """

        if self.list_frame is not None:
            self.list_frame.pack_forget()
            self.listbox.pack_forget()
            self.listbox = None
            self.scrollbar.pack_forget()
            self.scrollbar = None
            self.progress_bar.style = None
            self.collected = []
            self.list_frame = None
        elif self.sort_frame is not None:
            self.sort_frame.pack_forget()
            self.sort_frame = None
        position = f"{self._root.winfo_x()}+{self._root.winfo_y()}"
        self._root.geometry("318x118+" + position)
        self._root.config(bg=Player.BG)
        self.main_frame = Frame(self._root, bg=Player.BG, width=318, height=118)
        self.main_frame.pack()
        self.progress_bar = Scale(self.main_frame, from_=0, orient="horizontal", length=225,
                                command=self._slide, to=int(self.duration),
                                  cursor="hand2", variable=self._progress_variable)

        self.current_time = Label(self.main_frame, padx=0, text=self.ftime, width=7, anchor="e",
                                  bg=Player.BG, font=('arial', 9, 'bold'), fg=Player.FG)

        self._title = Button(self.main_frame, pady=0, bg=Player.BG, text=self._title_txt,
                            command=self._listview, width=44, height=1, relief="flat",
                            font=('arial', 8, 'bold'), fg=Player.FG, anchor=self._title_txt_anchor)
        self._title.place(x=0, y=1)

        self._shuffle = Button(self.main_frame, command=self.on_eos, text="SHUFFLE", padx=8,
                               bg=Player.BG, fg=Player.FG, font=("arial", 15, "bold"), relief="groove")
        self._shuffle.place(x=97, y=23)

        self._previous_btn = Button(self.main_frame, padx=0, bg=Player.BG, fg=Player.FG,
                                    command=self._play_prev_command, image=self.previous_img,
                                    font=("arial", 7, "bold"), relief="groove")

        self._play_btn = Button(self.main_frame, padx=0, bg=Player.BG,
                                command=self._play_btn_command, image=self.play_btn_img,
                                fg=Player.FG, font=("arial", 7, "bold"), relief="groove")

        self._next_btn = Button(self.main_frame, padx=0, bg=Player.BG,
                                command=self._play_next_command, image=self.next_img,
                                fg=Player.FG, font=("arial", 7, "bold"), relief="groove")


        self._repeat_btn = Button(self.main_frame, pady=0, padx=0, bg=Player.BG, width=20,
                                command=self._onoff_repeat, height=15,
                                  relief="flat", font=("arial", 6, "bold"), anchor="w")

        if Player.BG == "gray28":
            self.progress_bar.style = ThemedStyle()
            self.progress_bar.style.theme_use("equilux")
            self.progress_bar.place(x=52, y=92)
        elif Player.BG == "gray97":
            self.progress_bar.style = ThemedStyle()
            self.progress_bar.style.theme_use("arc")
            self.progress_bar.place(x=54, y=96)
        self.check_theme_mode()
        self._repeat_btn["image"] = self._repeat_image
        self._update_theme()

#------------------------------------------------------------------------------------------------------------------------------

    def _listview(self):
        """
            Listbox window
            Must be called only from or after self.main_frame
        """
        if self._active_repeat:
            self.image = PhotoImage(data=DARKREPEAT_IMG)
        else:
            self.image = PhotoImage(data=DARKSHUFFLE_IMG)
        self.main_frame.pack_forget()
        self.main_frame = None
        self._root.config(bg="white smoke")
        self.progress_bar.style = None
        self.list_frame = Frame(self._root, bg="gray28", width=310, height=94)
        self.list_frame.pack(fill="x", pady=0)

        self._title = Button(self.list_frame, pady=0, bg="gray28", text=self._title_txt,
                            command=self._init, anchor=self._title_txt_anchor,
                            font=('arial', 8, 'bold'), fg="white", width=44, relief="flat")
        self._title.place(x=1, y=1)

        self.current_time = Label(self.list_frame, padx=0, text=self.ftime, width=7, anchor="e",
                                  bg="gray28", font=('arial', 9, 'bold'), fg="white")
        self.current_time.place(x=30, y=25)

        self._previous_btn = Button(self.list_frame, padx=0, bg="gray28", fg="white",
                                    command=self._play_prev_command, image=self.previous_img,
                                    font=("arial", 7, "bold"), relief="groove")
        self._previous_btn.place(x=100, y=25)

        self._play_btn = Button(self.list_frame, padx=0, bg="gray28", image=self.play_btn_img,
                                command=self._play_btn_command,
                                fg="white", font=("arial", 7, "bold"), relief="groove")
        self._play_btn.place(x=150, y=25)

        self._next_btn = Button(self.list_frame, padx=0, bg="gray28",
                                command=self._play_next_command, image=self.next_img,
                                fg="white", font=("arial", 7, "bold"), relief="groove")
        self._next_btn.place(x=200, y=25)

        self._repeat_btn = Button(self.list_frame, bg="gray28", image=self.image,
                                    command=self._onoff_repeat, width=20, height=15, pady=0,
                                  relief="flat", font=("arial", 6, "bold"), anchor="w", padx=0,)
        self._repeat_btn.place(x=245, y=25)

        self.progress_bar = Scale(self.list_frame, from_=0, orient="horizontal", length=225,
                                     command=self._slide, to=int(self.duration),
                                  cursor="hand2", variable=self._progress_variable)
        if Player.BG != "gray28":
            self.progress_bar.style = ThemedStyle()
            self.progress_bar.style.theme_use("equilux")
        self.progress_bar.place(x=43, y=50)

        self.searchlabel = Label(self.list_frame, font=('arial', 8, 'bold'), text="Search:",
                            bg="gray28", fg="white")

        self.searchbar = Entry(self.list_frame, relief="flat", bg="gray40", fg="white",
                                insertbackground="white")
        self.searchbar.bind("<Return>", self._on_search)

        self.listbox = Listbox(self._root, bg="white smoke", fg="black", width=42, selectmode="extended",
                                selectbackground="DeepSkyBlue3", selectforeground="white",
                                height=36, relief="flat", font=('New Times Roman', 9), highlightthickness=0)

        self.scrollbar = Scrollbar(self._root, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.listbox.bind("<Double-Button-1>", self._on_click)
        self.listbox.bind("<Button-2>", self._listbox_rightclick)
        self.listbox.bind("<Button-3>", self._listbox_rightclick)
        self.listbox.bind("<MouseWheel>", self.scroll_widget)
        self.listbox.bind("<Return>", self._on_click)

        self._update_listbox()
        self._update_bindings()
        if self._active_repeat:
            ToolTip(self._repeat_btn, "Repeat One")
        else:
            ToolTip(self._repeat_btn, "Shuffle On")
        if self._playing:
            self.duration_tip = ToolTip(self.progress_bar, f"Duration: {timedelta(seconds=self.duration)}")

#------------------------------------------------------------------------------------------------------------------------------

    def _on_eop(self):
        """
            Done window
            Responsible for end of player dir chooser
        """

        if self.list_frame is not None:
            self.list_frame.pack_forget()
            self.listbox.pack_forget()
            self.scrollbar.pack_forget()
            self.progress_bar.style = None
            self.list_frame = None
        elif self.main_frame is not None:
            self.main_frame.pack_forget()
            self.main_frame = None
        self._root.geometry("318x116+" + f"{self._root.winfo_x()}+{self._root.winfo_y()}")
        self._root.config(bg="gray94")
        self.done_frame = Frame(self._root, bg="gray94", width=310, height=116)
        self.done_frame.pack(padx=3, pady=5)
        self.repeat_folder_img = PhotoImage(data=REPEATFOLDER_IMG)
        self.add_folder_img = PhotoImage(data=ADDFOLDER_IMG)

        description = Label(self.done_frame, bg="gray94", width=300,
                            text="Repeat Folder             Add New Folder")
        description.pack(side="top", pady=10)
        self.repeat_folder = Button(self.done_frame, image=self.repeat_folder_img,
                                command=self._repeat_ended, relief="flat")
        self.repeat_folder.pack(padx=70, pady=0, side="left")
        self.add_folder = Button(self.done_frame, image=self.add_folder_img,
                            command=self._manual_add, relief="flat")
        self.add_folder.pack(padx=0, pady=0, side="left")

#------------------------------------------------------------------------------------------------------------------------------

    def _on_sort(self):

        if self.list_frame is not None:
            self.list_frame.pack_forget()
            self.listbox.pack_forget()
            self.scrollbar.pack_forget()
            self.progress_bar.style = None
            self.list_frame = None
        elif self.main_frame is not None:
            self.main_frame.pack_forget()
            self.main_frame = None
        elif self.done_frame is not None:
            self.done_frame.pack_forget()
            self.done_frame = None
        color = "gray90"
        try:
            position = Player._CONFIG["window"]["position"]
        except KeyError:
            position = f"{self._root.winfo_x()}+{self._root.winfo_y()}"
        self._root.geometry("318x116+" + position)
        self._root.config(bg=color)
        self.sort_frame = Frame(self._root, bg=color, width=310, height=116)
        self.sort_frame.pack(padx=3, pady=5)
        dsp = Label(self.sort_frame, bg=color, font=("New Times Roman", 9, "bold"),
                    text="Type artist names whose songs will play first\n(separate words by space)")
        dsp.place(x=18, y=5)

        cancel_btn = Button(self.sort_frame, text="Cancel", bg=color, anchor="center", command=self._init)
        cancel_btn.place(x=18, y=80)
        ToolTip(cancel_btn, "Use default shuffle")
        ok_btn = Button(self.sort_frame, text="OK", bg=color, command=self._sort_by_keys, padx=10, pady=1, anchor="center")
        ok_btn.place(x=237, y=80)

        label1 = Label(self.sort_frame, bg=color, text="Artist names:",
                        font=("New Times Roman", 9, "bold"), anchor="e")
        label1.place(x=15, y=50)
        self.keywords_shelf = Entry(self.sort_frame, bg="gray94", relief="groove", width=30)
        self.keywords_shelf.place(x=98, y=52)
        self.keywords_shelf.bind("<Return>", self._sort_by_keys)

#------------------------------------------------------------------------------------------------------------------------------

    def _on_click(self, event=None):
        """
            Plays songs clicked from listbox directly
            Tries to mimic on_eos functionalities
        """

        try:
            self._start = 0
            index = self.listbox.curselection()[-1]
            if len(self.collected) == 0:
                self._song = join(self._songspath, self._all_files[index])
                self.index = index
            else:
                self._song = join(self._songspath, self.collected[index])
                self.collection_index = index

            if debug: print("Index:", self.collection_index, self._song)
            self._mixer(self._song).play()
            try: # in case shuffle_mixer is NoneType
                self._updating()
            except AttributeError:
                pass
            self.play_btn_img = self.pause_img
            self._play_btn["image"] = self.play_btn_img
            self._set_thread(self._run_event, "Pyglet Event").start()
            self._playing = True
            if self._song == "Unreadable File":
                self._playing = False
        except IndexError:
            pass

#------------------------------------------------------------------------------------------------------------------------------

    def _change_place(self):
        """
            Switches slider to above or below
        """

        if self.main_frame is not None:
            if self._slider_above:
                if Player.BG == "gray28":
                    timeandbtn = 94
                    pb = 92
                else:
                    pb = 96
                    timeandbtn = 94
                controls = 68
            else:
                if Player.BG == "gray28":
                    timeandbtn = 66
                    pb = 64
                else:
                    pb = 68
                    timeandbtn = 66
                controls = 86
            self.progress_bar.place(x=54, y=pb)
            self.current_time.place(x=0, y=timeandbtn)
            self._previous_btn.place(x=115, y=controls)
            self._play_btn.place(x=145, y=controls)
            self._next_btn.place(x=175, y=controls)
            self._repeat_btn.place(x=280, y=timeandbtn)
            self._root.update()
            self._slider_above = not self._slider_above

#------------------------------------------------------------------------------------------------------------------------------

    def _update_theme(self):
        """
            Updates slider according to the color chosen
            Places widgets in their correct positions
        """

        if Player.BG == "gray28":
            self._update_bindings()
            self.progress_bar.style = ThemedStyle()
            self.progress_bar.style.theme_use("equilux")
            if not self._slider_above: # Restore slider to default
                self._previous_btn.place(x=115, y=68)

                self._play_btn.place(x=145, y=68)

                self._next_btn.place(x=175, y=68)

                self.progress_bar.place(x=52, y=92)
                self.current_time.place(x=0, y=94)
                self._repeat_btn.place(x=280, y=94)
            else:
                self._previous_btn.place(x=115, y=86)
                self._play_btn.place(x=145, y=86)
                self._next_btn.place(x=175, y=86)
                self.current_time.place(x=0, y=66)
                self._repeat_btn.place(x=280, y=66)
                self.progress_bar.place(x=52, y=64)
        else:
            self._tips()
            self.progress_bar.style = ThemedStyle()
            self.progress_bar.style.theme_use("arc")
            if not self._slider_above:
                self._previous_btn.place(x=115, y=68)

                self._play_btn.place(x=145, y=68)

                self._next_btn.place(x=175, y=68)

                self.progress_bar.place(x=54, y=96)
                self.current_time.place(x=0, y=94)
                self._repeat_btn.place(x=280, y=94)
            else:
                self._previous_btn.place(x=115, y=86)
                self._play_btn.place(x=145, y=86)
                self._next_btn.place(x=175, y=86)
                self.current_time.place(x=0, y=66)
                self._repeat_btn.place(x=280, y=66)
                self.progress_bar.place(x=54, y=68)

        self.main_frame["bg"] = Player.BG
        self._repeat_btn["bg"], self._repeat_btn["fg"] = Player.BG, Player.FG
        self._play_btn["bg"], self._play_btn["fg"] = Player.BG, Player.FG
        self._next_btn["bg"], self._next_btn["fg"] = Player.BG, Player.FG
        self._shuffle["bg"], self._shuffle["fg"] = Player.BG, Player.FG
        self._previous_btn["bg"], self._previous_btn["fg"] = Player.BG, Player.FG
        self.current_time["bg"], self.current_time["fg"] = Player.BG, Player.FG
        self._title["bg"], self._title["fg"] = Player.BG, Player.FG
        self.file_menu["bg"], self.file_menu["fg"] = Player.BG, Player.FG
        self.theme_menu["bg"], self.theme_menu["fg"] = Player.BG, Player.FG
        self.about_menu["bg"], self.about_menu["fg"] = Player.BG, Player.FG

#------------------------------------------------------------------------------------------------------------------------------

    def _manual_add(self):
        """
            Calls refresher function with open folder set to true
        """

        self._open_folder = True
        self._refresher()

#------------------------------------------------------------------------------------------------------------------------------

    def _repeat_ended(self):
        """
            Repeats playing songs in the just ended folder
        """

        all_files = listdir(self._songspath)
        self._all_files = [i for i in all_files if i.endswith(self.__supported_extensions)]
        shuffle(self._all_files)
        if self.done_frame is not None:
            self.done_frame.pack_forget()
            self.done_frame = None
            self._init()
            self.collection_index = None
            self.index = -1
            self.on_eos()

#------------------------------------------------------------------------------------------------------------------------------

    def _refresher(self):
        """
            Updates folder files where necessry, or those passed as CL arguments
            Updates the title of window
            Shuffles the playlist
        """

        self.collection_index = None
        all_files = []
        if len(PASSED_FILES) > 0:
            if debug: print(PASSED_FILES)
            self._all_files = [i for i in PASSED_FILES if i.endswith(self.__supported_extensions)]
            self._songspath = dirname(self._all_files[0])
            PASSED_FILES.clear()
            t = basename(self._songspath) if len(basename(self._songspath)) != 0 else "Disk"
            self._root.title(f"Lazy Selector - {t}".ljust(29))
            self.on_eos()
        else:
            try:
                # try getting the previous folder
                file = Player._CONFIG["files"]["folder"]
                self._songspath = file
            except KeyError:
                file = ""
            if (self._open_folder) or (not exists(file)):
                self._songspath = askdirectory(
                        title="Choose a Folder with Audio Files", initialdir=expanduser("~\\"))
                # file = self._songspath  # get the folder
            if (file == self._songspath) and (self._all_files != []):
                # don't update the songs list
                pass
            else:
                # update
                try:
                    all_files = listdir(self._songspath)

                except FileNotFoundError: # if Cancel clicked in the dialog
                    # if log file isn't empty and songs list is empty, update playlist
                    if (file != "") and (self._all_files == []):
                        self._songspath = file
                        all_files = listdir(self._songspath)
                    # if no directory was chosen and songs list isn't empty, no updating playlist
                    elif (self._songspath == "") and (self._all_files != []):
                        self._songspath = file
                    else:
                        if askokcancel("Lazy Selector",
                                       "\tA folder is required!\n    Do you want to select a folder again?"):
                            self._open_folder = True
                            self._refresher()
                        else:
                            self._root.destroy()
                            exit()
        if len(all_files) > 0:
            self.index = -1
            try:
                Player._CONFIG.add_section("files")
            except Exception:
                pass
            Player._CONFIG.set("files", "folder", self._songspath) # save to config file
            self._root.title("LOADING...")
            self._all_files = [i for i in all_files if i.endswith(self.__supported_extensions)]
            shuffle(self._all_files)
            t = basename(self._songspath) if len(basename(self._songspath)) != 0 else "Disk"
            self._root.title(f"Lazy Selector - {t}".ljust(29))

            self._on_sort()
        if not self._playing and self.shuffle_mixer._audio_player is None:
            self.collection_index = None
            self._start = 0
            self._progress_variable.set(self._start)
            self.ftime = "00:00"
            self.current_time["text"] = self.ftime
            self._title_txt = ""
            self._title["text"] = self._title_txt
            self.play_btn_img = self.play_img
            self._play_btn["image"] = self.play_btn_img
            self._play_btn_command = self._unpause
            self._play_next_command = None
            self._play_prev_command = None
            self._play_btn["command"] = self._play_btn_command
            self._previous_btn["command"] = self._play_prev_command
            self._next_btn["command"] = self._play_next_command
            print("Configured to 0")

#------------------------------------------------------------------------------------------------------------------------------

    def _loader(self):
        """
            Yields the path to song
            Removes the file from the main playlist
            Deletes the filename from listbox then resizes it
        """

        self.index += 1
        try:
            i = self._all_files[self.index]
        except IndexError:
            return False
        if i.endswith(self.__supported_extensions):
            filepath = join(self._songspath, i)
            if self.list_frame is not None and not len(self.collected):
                self.listbox.selection_clear("end", 0)
                self.listbox.selection_set(self.index)
                self.listbox.see(self.index)
        else:
            pass

        try:
            return filepath
        except Exception as e:
            pass

#------------------------------------------------------------------------------------------------------------------------------

    def _select_fav(self):
        """
            Asks the user for filenames input
        """

        loaded_files = askopenfilenames(title="Choose Audio files",
                                        filetypes=[("MP3 audio","*.mp3"),
                                        ("M4A audio","*.m4a"),
                                        ("AAC audio","*.aac")],
                                        initialdir=expanduser("~\\Music"),
                                        defaultextension="*.mp3")
        if len(loaded_files) != 0 and len(self._loaded_files) == 0:
            self._loaded_files = [i for i in loaded_files]

        else:
            for a in loaded_files:
                self._loaded_files.append(a)

        for audio in self._loaded_files:
            song = basename(audio)
            if song in self._all_files:
                index = self._all_files.index(song)
                self._all_files.remove(song)
                if self.listbox is not None:
                    self.listbox.delete(index)
        if len(loaded_files) >= 1:
            self._files_selected = True
        else:
            self._files_selected = False

#------------------------------------------------------------------------------------------------------------------------------

    def _load_files(self):
        """
            Yields a path of songs added to queue by Add to Queue function
            Removes the song from list
        """

        for i in self._loaded_files:
            yield self._loaded_files.pop(0) # get the first item in list

#------------------------------------------------------------------------------------------------------------------------------

    def _mixer(self, load):
        """
            Pyglet mixer engine
        """

        self.shuffle_mixer.pause()
        self.shuffle_mixer = None
        self.shuffle_mixer = p_mixer()
        try:
            source = p_load(load)
            m = source.get_format().meta
            if m[0] == 1 and m[1] == 44100: # for 44100Hz mono channel
                self.shuffle_mixer.pitch = 2.0
            else:
                self.shuffle_mixer.pitch = 1.0
            self.shuffle_mixer.queue(source)
            self.duration = round(self.shuffle_mixer.source.duration)
            if self._active_repeat:
                self.shuffle_mixer.loop = True
            return self.shuffle_mixer
        except Exception:
            notification.notify(title="Lazy Selector",
                                message=f"{basename(load)} is Unreadable!",
                                app_name="Lazy Selector",
                                timeout=5,
                                app_icon=DATA_DIR + "\\app.ico")
            self._song = "Unreadable File"
            self._title_txt_anchor = "center"
            self._progress_variable.set(0)
            self.progress_bar.config(variable=0)
            self.progress_bar.update()
            self.ftime = "00:00"
            self.current_time["text"] = self.ftime
            return self.shuffle_mixer

#------------------------------------------------------------------------------------------------------------------------------

    def on_eos(self):
        """
            Play on shuffle
        """

        self._start = 0
        self._playing = False
        self.play_btn_img = self.pause_img
        self._play_btn["image"] = self.play_btn_img

        if not self._files_selected:


            self._song = self._loader()
            if self._song:
                try: # If the player fails the first time
                    self._mixer(self._song).play()
                except ValueError: # High chances it won't fail twice
                    self._song = self._loader()
                    if self._song:
                        self._mixer(self._song).play()

        elif self._files_selected:
            try:
                self._song = next(self._load_files())
                try:
                    self._mixer(self._song).play()
                except ValueError:
                    self._song = next(self._load_files())
                    self._mixer(self._song).play()
            except StopIteration: # if it ever catches the error
                pass
            if len(self._loaded_files) == 0: # avoid catching the StopIteration error above
                self._files_selected = False

        if self._song:
            self._set_thread(self._run_event, "Pyglet Event").start()
            try: # in case shuffle_mixer is NoneType
                self._updating()
            except AttributeError:
                pass

        self._playing = True

        if not self._song and not self.index: # if self.index never incremented in self._loader/_load_files/self._on_click
            if self.shuffle_mixer._audio_player is None:
                self._playing = False

            try:
                showinfo(
                    "Lazy Selector",
                    f"{basename(self._songspath) if len(basename(self._songspath)) != 0 else 'Disk'} "
                    "folder has no Audio files.\n\n   Choose a different Folder.")
            except AttributeError: # if self._songspath never initialized
                showinfo("Lazy Selector", "No folder initialized!")
            self._manual_add()

        elif not self._song and self.index > len(self._all_files) - 1:

            self._stop_play()
            self._on_eop()
        if self._song == "Unreadable File":
            self._all_files.remove(self._all_files[self.index])
            self._playing = False
            sleep(0.1)
            self.on_eos()

#------------------------------------------------------------------------------------------------------------------------------

    def _updating(self):
        """
            Manages already played
        """

        try: # If it's not first time of calling this function
            self.duration_tip.unschedule()
            self.duration_tip.hidetip()
        except AttributeError:
            pass
        self.duration_tip = ToolTip(self.progress_bar, f"Duration: {timedelta(seconds=self.duration)}")
        self._play_prev_command = lambda: self._play_prev()
        self._play_next_command = lambda: self._play_prev(prev=False)
        self._play_btn_command = self._stop_play
        self._previous_btn["command"] = self._play_prev_command
        self._play_btn["command"] = self._play_btn_command
        self._next_btn["command"] = self._play_next_command
        self._title_txt = self._convert(splitext(basename(self._song))[0])
        self.progress_bar["to"] = int(self.duration)
        self._update_labels(self._title_txt)

#------------------------------------------------------------------------------------------------------------------------------

    def _play_prev(self, prev=True):
        """
            Play previous or next
        """

        self.play_btn_img = self.pause_img
        self._play_btn["image"] = self.play_btn_img
        self._playing = False
        self._start = 0
        if prev:
            if len(self.collected):
                self.collection_index -= 1
                if self.collection_index < 0:
                    self.collection_index = 0
                i = self.collected[self.collection_index]
            else:
                self.index -= 1
                if self.index < 0:
                    self.index = 0
                i = self._all_files[self.index]
            self._song = join(self._songspath, i)
        else:
            if len(self.collected):
                self.collection_index += 1
                if self.collection_index > len(self.collected) - 1:
                    self.collection_index = len(self.collected) - 1
                i = self.collected[self.collection_index]
            else:
                self.index += 1
                if self.index > len(self._all_files) - 1:
                    self.index = len(self._all_files) - 1
                i = self._all_files[self.index]
            self._song = join(self._songspath, i)

        if self.list_frame is not None:
            if self.collection_index is not None:
                prev_index = self.collection_index
                self.listbox.selection_clear("end", 0)
                self.listbox.selection_set(prev_index)
                self.listbox.see(prev_index)
            else:
                prev_index = self.index
                self.listbox.selection_clear("end", 0)
                self.listbox.selection_set(prev_index)
                self.listbox.see(prev_index)
        self._mixer(self._song).play()
        try: # in case shuffle_mixer is NoneType
            self._updating()
        except AttributeError:
            pass
        self._playing = True
        if self._song == "Unreadable File":
            self._playing = False
            showinfo("Lazy Selector", "File may have been moved or deleted!")
            self.on_eos()

#------------------------------------------------------------------------------------------------------------------------------

    def _onoff_repeat(self):
        """
            Toggle player loop
        """

        self._active_repeat = not self._active_repeat
        self.shuffle_mixer.loop = self._active_repeat
        self.check_theme_mode()

#------------------------------------------------------------------------------------------------------------------------------

    def check_theme_mode(self):
        """
            Change repeat img according to theme set
            Update tooltips
        """
        if self._playing:
            self.duration_tip = ToolTip(self.progress_bar, f"Duration: {timedelta(seconds=self.duration)}")
        if self.main_frame is not None:
            ToolTip(self._shuffle, "Play Queued songs")
            ToolTip(self._title, "Show Playlist")
        if Player.BG == "gray97" and self.main_frame is not None:
            self._tips()
            if self._active_repeat:
                im = REPEAT_IMG
                ToolTip(self._repeat_btn, "Repeat One")
            else:
                ToolTip(self._repeat_btn, "Shuffle On")
                im = SHUFFLE_IMG
        else:
            if self._active_repeat:
                im = DARKREPEAT_IMG
                ToolTip(self._repeat_btn, "Repeat One")
            else:
                ToolTip(self._repeat_btn, "Shuffle On")
                im = DARKSHUFFLE_IMG
        self._repeat_image = PhotoImage(data=im)
        self._repeat_btn["image"] = self._repeat_image

#------------------------------------------------------------------------------------------------------------------------------

    def _run_event(self):
        """
            Pyglet event loop
        """

        from pyglet.app import run # to avoid thread error
        try:
            run()
        except Exception:  # RuntimeError, ReferenceError
            pass

#------------------------------------------------------------------------------------------------------------------------------

    def _kill(self):
        """
            Confirm exit if playing, save modifications
        """

        try:
            chmod(DATA_DIR + "\\lazylog.cfg", S_IWUSR | S_IREAD)
        except Exception:
            pass
        if self._playing:
            if askokcancel("Lazy Selector", "Music is still playing.\n      Quit Anyway?"):
                self._stop_play()

                try:
                    Player._CONFIG.add_section("window")
                except Exception:
                    pass
                Player._CONFIG.set("window", "position", f"{self._root.winfo_x()}+{self._root.winfo_y()}")
                try:
                    with open(DATA_DIR + "\\lazylog.cfg", "w") as f:
                        Player._CONFIG.write(f)
                except Exception as er:
                    pass
                chmod(DATA_DIR + "\\lazylog.cfg", S_IREAD | S_IRGRP | S_IROTH)
                self.shuffle_mixer.delete()
                self._root.destroy()
                exit()
        else:
            try:
                Player._CONFIG.add_section("window")
            except Exception:
                pass
            Player._CONFIG.set("window", "position", f"{self._root.winfo_x()}+{self._root.winfo_y()}")
            try:
                with open(DATA_DIR + "\\lazylog.cfg", "w") as f:
                    Player._CONFIG.write(f)
            except Exception as er:
                pass
            chmod(DATA_DIR + "\\lazylog.cfg", S_IREAD | S_IRGRP | S_IROTH)
            self.shuffle_mixer.delete()
            self._root.destroy()
            exit()

#------------------------------------------------------------------------------------------------------------------------------

    def _convert(self, text):
        """
            Trims and removes emoji not supported by tkinter
        """

        elem = [i if ord(i) < 65535 else "." for i in text]
        if len(elem) > 53: # not so perfect
            elem = elem[:51] + ["..."]

        return "".join(elem)

#------------------------------------------------------------------------------------------------------------------------------

    def _update_labels(self, song):
        """
            Updates all labels that need update on change of song
            Aligns the title text
        """

        if song == "MUSIC PAUSED" or len(song) <= 49:
            self._title_txt_anchor = "center"
            self._title["anchor"] = self._title_txt_anchor
        else:
            self._title_txt_anchor = "w"
            self._title["anchor"] = self._title_txt_anchor
        self._title["text"] = song

#------------------------------------------------------------------------------------------------------------------------------

    def _about(self):
        """
            Shows information about the player
        """

        if self.top is None:
            self.top = Toplevel()
            self.top.wm_protocol("WM_DELETE_WINDOW", self._kill_top)
            self.top.wm_title("Lazy Selector - About")
            position = f"{self._root.winfo_x() - 40}+{self._root.winfo_y()}"
            self.top.geometry("400x630+" + position)
            self.top.resizable(0, 0)
            self.display_text = Label(self.top, pady=10, padx=50, text="Lazy Selector\nVersion: 4.1\nDeveloped by: Ernesto\nernestondieki12@gmail.com",
                                    font=("arial",12), relief="groove")
            self.display_text.pack(pady=10)
            self.display_canvas = Canvas(self.top, height=3010)
            self.top_scrollbar = Scrollbar(self.top, command=self.display_canvas.yview)
            self.display_canvas.config(yscrollcommand=self.top_scrollbar.set)
            self.top_scrollbar.pack(side="right", fill="y")
            self.display_canvas.pack(expand=True)

            self.image1 = PhotoImage(data=LIGHTWINDOW1_IMG)
            self.display_canvas.create_text(40, 10, text="1. Light themed window", anchor="w")
            self.display_canvas.create_image(40, 20, image=self.image1, anchor="nw")

            self.image2 = PhotoImage(data=DARKWINDOW1_IMG)
            self.display_canvas.create_text(40, 220, text="2. Dark themed window", anchor="w")
            self.display_canvas.create_image(40, 230, image=self.image2, anchor="nw")

            self.image3 = PhotoImage(data=FILEOPTIONS_IMG)
            self.display_canvas.create_text(40, 425, text="3. File options. 'Add to Queue' adds songs from different folders\nSupports mp3, m4a, aac files", anchor="w")
            self.display_canvas.create_image(40, 440, image=self.image3, anchor="nw")

            self.image4 = PhotoImage(data=HELPOPTIONS_IMG)
            self.display_canvas.create_text(40, 640, text="4. 'Switch Slider' positions slider either above or below controls", anchor="w")
            self.display_canvas.create_image(40, 650, image=self.image4, anchor="nw")

            self.image5 = PhotoImage(data=DURATIONTIP_IMG)
            self.display_canvas.create_text(40, 850, text="5. Place the mouse on the slider to view song duration", anchor="w")
            self.display_canvas.create_image(40, 860, image=self.image5, anchor="nw")

            self.image8 = PhotoImage(data=REPEATTIP_IMG)
            self.display_canvas.create_text(40, 1270, text="6. Click to repeat one song infinitely or shuffle by default", anchor="w")
            self.display_canvas.create_image(10, 1280, image=self.image8, anchor="nw")

            self.image6 = PhotoImage(data=RIGHTCLICK_IMG)
            self.display_canvas.create_text(40, 1490,
                                            text="7. Right-click on selected song for more operations.\nOr press Enter/Double-click to play\n'Play Next' only works for songs below the currently playing",
                                            anchor="w")
            self.display_canvas.create_image(40, 1520, image=self.image6, anchor="nw")

            self.image9 = PhotoImage(data=KEYWORDSIN_IMG)
            self.display_canvas.create_text(40, 1950, text="8. Prioritize artist songs in your playlist", anchor="w")
            self.display_canvas.create_image(40, 1960, image=self.image9, anchor="nw")

            self.image10 = PhotoImage(data=KEYWORDSSORTEDLIST_IMG)
            self.display_canvas.create_text(40, 2200, text="9. Songs of artists (typed above) come on top of the list", anchor="w")
            self.display_canvas.create_image(40, 2210, image=self.image10, anchor="nw")


            self.image7 = PhotoImage(data=INLISTBOXSEARCH_IMG)
            self.display_canvas.create_text(40, 2990, text="10. Search songs and artists in the playlist\nResulting playlist plays in loop mode", anchor="w")
            self.display_canvas.create_image(40, 3010, image=self.image7, anchor="nw")
            self.display_canvas.bind("<MouseWheel>", self.scroll_widget)

            self.image11 = PhotoImage(data=SOKORO_IMG)
            self.display_canvas.create_text(100, 3430, text="In loving memory of grandpa, Joseph", anchor="w", font=("New Times Roman", 10, "italic bold"))
            self.display_canvas.create_image(180, 3440, image=self.image11, anchor="nw")
            self.display_canvas.config(scrollregion=self.display_canvas.bbox("all"))

#------------------------------------------------------------------------------------------------------------------------------

    def _kill_top(self):
        self.top.destroy()
        self.top = None

#------------------------------------------------------------------------------------------------------------------------------

    def _update_color(self, bg, fg):
        """
            Switches between themes
            Usage: self._update_color(background:str, foreground:str)
        """

        if self.main_frame is not None:
            Player.BG = bg
            Player.FG = fg
            Player.MN = bg
            try:
                Player._CONFIG.add_section("theme")
            except Exception:
                pass
            Player._CONFIG.set("theme", "bg", Player.BG)
            Player._CONFIG.set("theme", "fg", Player.FG)
            self.check_theme_mode()
            self._update_theme()

#------------------------------------------------------------------------------------------------------------------------------

    def _stop_play(self):
        """
            Pauses playback
        """
        if self._play_btn_command is not None:
            self._play_btn["state"] = "disabled"
            self.play_btn_img = self.play_img
            self._play_btn_command = self._unpause
            self._playing = False
            self._play_btn["image"] = self.play_btn_img
            self._play_btn["command"] = self._play_btn_command
            self._update_labels(self._title_txt)
            self.shuffle_mixer.pause()
            self._play_btn["state"] = "normal"

    def _unpause(self):
        """
            Resumes playback
        """

        if self._play_btn_command is not None and self.shuffle_mixer._audio_player is not None:
            self._play_btn_command = self._stop_play
            self.play_btn_img = self.pause_img
            self._play_btn["image"] = self.play_btn_img
            self._play_btn["command"] = self._play_btn_command
            self._update_labels(self._title_txt)
            self.shuffle_mixer.play()
            self._playing = True
        elif self.shuffle_mixer._audio_player is None:
            self.on_eos()

#------------------------------------------------------------------------------------------------------------------------------

    def _set_thread(self, func, nm, c=()):
        """
            setup a daemon thread
        """

        return Thread(target=func, args=c, daemon=True, name=nm)

#------------------------------------------------------------------------------------------------------------------------------

    def _slide(self, value):
        """
            Seeks and updates value of slider
        """

        if self._playing:
            self._playing = False
            self._progress_variable.set(round(float(value)))
            pos = self._progress_variable.get()
            sleep(0.1) # let the slider breathe... not a smooth sliding experience
            self._start = pos
            self.shuffle_mixer.seek(round(float(value)))
            self._playing = True
        else:
            self._progress_variable.set(value)

#------------------------------------------------------------------------------------------------------------------------------

    def _set_uptime(self):
        """
            Updates current time and checks for eos and battery
        """

        said = False
        while True:

            if (self.shuffle_mixer._audio_player is None and self._start > 3 and not self._active_repeat) or \
                (self._start >= self.duration - 1 and not self._active_repeat):

                if len(self.collected) > 0 and self.list_frame is not None and self.collection_index is not None:
                    self.collection_index += 1
                    self.listbox.selection_clear("end", 0)
                    self._collection_manager()
                else:
                    self.on_eos()
                self._root.update_idletasks()
            elif self._playing and self.shuffle_mixer._audio_player is not None:
                self._start = round(self.shuffle_mixer.time)
                if self._start >= 3600:
                    self._root.update_idletasks()
                    self.ftime = timedelta(seconds=self._start)
                else:
                    mins, secs = divmod(self._start, 60)
                    self.ftime = f"{round(mins):02}:{round(secs):02}"

                self.current_time.config(text=self.ftime)
                self._progress_variable.set(self._start)
                sleep(0.98)
                if battery.get_state()["percentage"] < 41 and not said:
                    # a reminder
                    notification.notify(title="Lazy Selector",
                                        message=f'{battery.get_state()["percentage"]}% Charge Available',
                                        app_name="Lazy Selector",
                                        timeout=180,
                                        app_icon=DATA_DIR + "\\app.ico")
                    said = True

            else:
                if battery.get_state()["percentage"] < 41 and not said:
                    # a reminder
                    notification.notify(title="Lazy Selector",
                                        message=f'{battery.get_state()["percentage"]}% Charge Available',
                                        app_name="Lazy Selector",
                                        timeout=180,
                                        app_icon=DATA_DIR + "\\app.ico")
                    said = True
                sleep(0.4) # slight unnoticeable delay from unpausing

#------------------------------------------------------------------------------------------------------------------------------

    def _collection_manager(self):
        """
            Plays, increments index and loops in searched songs
        """

        if self.collection_index > len(self.collected) - 1:
            self._playing = False
            self.collection_index = -1
            print("Index: 0")
        else:
            if debug: print("Collection Manager Index after:", self.collection_index)
            self.listbox.selection_set(self.collection_index)
            self.listbox.see(self.collection_index)
            self._on_click()

#------------------------------------------------------------------------------------------------------------------------------

    def __prioritize(self, sequence=None, keywords=None):
        """
            Insert match of sequence at index 0
        """
        if debug: print(keywords)
        if keywords is None or len(keywords) < 3 or keywords == "":
            pass
        else:
            keys = keywords.strip().split(" ")
            if debug: print(keys)
            for item in sequence:
                i = SPLIT("[- _.]", item.lower())
                for keyword in keys:
                    if keyword.lower() in i:
                        sequence.remove(item)
                        sequence.insert(0, item)

#--------------------------------------------------------------------------------------------------------------------------------

    def _sort_by_keys(self, event=None):

        keys = self.keywords_shelf.get()
        self.__prioritize(self._all_files, keywords=keys)
        self._init()

PASSED_FILES = sys.argv[1:]

pid = process_exists("Lazy_Selector.exe")
if debug: print(pid)
if pid and getpid() != pid:
    try:
        kill(pid, 0)
    except SystemError as o:
        if debug: print(o)
        pass
tk = Tk()
p = Player(tk)
tk.mainloop()
# try:
#     tk = Tk()
#     Player(tk)
#     tk.mainloop()
# except Exception:
#     tk.destroy()
#     exit([1])
#TODO
# pass song to queue of already playing player