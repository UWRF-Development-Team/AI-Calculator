import tkinter as tk

root = tk.Tk()

canvas = tk.Canvas(root, width=640, height=320)
canvas.grid(row = 0, column = 0)

root.minsize(640, 320)
root.title("AI Calculator")

old_x = None
old_y = None

def on_mouse_move(event):
    global old_x
    global old_y
    x = event.x
    y = event.y
    old_x = x if old_x is None else old_x
    old_y = y if old_y is None else old_y
    canvas.create_line(old_x, old_y, x, y, fill="black")
    old_x = x
    old_y = y

def on_mouse_release(event):
    global old_x
    global old_y
    old_x = None
    old_y = None

canvas.bind("<B1-Motion>", on_mouse_move)
canvas.bind("<ButtonRelease-1>", on_mouse_release)

root.mainloop()