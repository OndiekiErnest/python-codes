__author__ = "Ernesto"
__email__ = "ernestondieki12@gmail.com"

from time import strftime
from tkinter import Label, Tk, Frame


class Watch:
    """
        Create a digital watch
    """

    # Called first when the class is instantiated
    def __init__(self, root: Tk):
        # set common attributes
        self.foreground_color = "red"
        self.background_color = "black"
        # startup User Interface
        self.gui(root)
        # set the time/date to their respective labels
        self.update_time()

    # Let's define the methods called above
    def gui(self, window):
        """Initialize the Watch User Interface"""

        self.root = window
        self.root.title("TODAY")
        # Window position in the format (Height x Width + X-axis + Y-axis)
        self.root.geometry("450x230+200+450")
        # disable resizing
        self.root.resizable(0, 0)
        # create time label and set its attributes
        self.time_label = Label(self.root,
                                relief="groove",
                                bg=self.background_color,
                                fg=self.foreground_color,
                                font=("Gill Sans MT Condensed", 121, "bold")
                                )
        # map the time label to the screen
        self.time_label.place(x=10, y=10)
        # create frame to manage other widgets separately
        self.date_frame = Frame(self.root)
        # map the frame to the screen
        self.date_frame.place(x=12, y=12)
        # create date label and set its attributes
        self.date_label = Label(self.date_frame,
                                bg=self.background_color,
                                fg=self.foreground_color,
                                width=46,
                                anchor="e",
                                font=("Gill Sans MT Condensed", 19, "bold")
                                )
        # map the date label to the frame
        self.date_label.pack()

    def __str__(self):
        """Called when printing the instance of the class (line 70)"""

        return f"{self.now_time} - {self.now_date}"

    def update_time(self) -> Tk.after:
        """Updates time/date to the screen every one second"""

        # format the current time (HH:MM:SS)
        self.now_time = strftime("%H:%M:%S")
        # format the current date (Date of Month, Year)
        self.now_date = strftime("%d of %b, %Y")
        # set the time/date to the screen (widgets)
        self.date_label.config(text=self.now_date)
        self.time_label.config(text=self.now_time)
        # Call this function repeatedly after every 1000 ms (1 second)
        return self.root.after(1000, self.update_time)


if __name__ == '__main__':

    tk = Tk()
    r = Watch(tk)
    tk.mainloop()
    print(r)
