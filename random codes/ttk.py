from tkinter import*
from tkinter import ttk
import os, time, random
root=Tk()
label=ttk.Label(root)
label.pack()

files=os.listdir('C:\\Users\code\Pictures')

for picName in files:
    pic=files[random.randint(0, len(files)-1)]
    if pic.endswith('.PNG'):
        fileSelect=os.path.join('C:\\Users\code\Pictures',pic)
        logo=PhotoImage(file=fileSelect)
        label.config(image=logo, wraplength=150, compound='center')
        files.remove(pic)
        break
    else:
        continue
    

root.mainloop()


