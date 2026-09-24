import tkinter as tk

root = tk.Tk()

canvas = tk.Canvas(root, width=640, height=320)
canvas.grid(row = 0, column = 0, sticky = tk.NSEW)

root.minsize(640, 320)
root.title("AI Calculator")

def on_mouse_move(event):
    x = event.x
    y = event.y
    print (x, y)
    canvas.create_rectangle(x, y, x, y, fill="black")

canvas.bind("<B1-Motion>", on_mouse_move)

root.mainloop()