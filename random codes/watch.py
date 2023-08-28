from time import strftime
from tkinter import*

wn = Tk()
wn.geometry("450x230+900+500")
wn.title("TODAY".ljust(70))
wn.resizable(width=False,height=False)
now_date = strftime("%d of %b, %Y")

time_label = Label(wn, relief=GROOVE,bg="black",fg="red",
					font=("Gill Sans MT Condensed",121,"bold"))
time_label.place(x=10,y=10)

frame = Frame(wn)
frame.place(x=12,y=12)
date_label = Label(frame,bg="black",fg="red",width=46,anchor=E,
					font=("Gill Sans MT Condensed",19,"bold"),text=now_date)
date_label.pack()

def cur_time():
	now_time = strftime("%H:%M:%S")
	time_label["text"] = now_time
	run_again = wn.after(1000,cur_time)
cur_time()

wn.mainloop()
