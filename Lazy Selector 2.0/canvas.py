

from tkinter import Canvas, Tk

root = Tk()

canvas = Canvas(root,bg="black",width=500,height=400)
canvas.pack()
box = canvas.create_rectangle(100,50,100,50,fill="white")
root.update()

root.mainloop()

