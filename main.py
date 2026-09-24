import tkinter as tk
from typing import assert_type
from pathlib import Path

from PIL import Image, ImageDraw

root = tk.Tk()

# For the user to see
canvas = tk.Canvas(root, width=640, height=320)
canvas.grid(row = 0, column = 0)

text_input = tk.Entry(root)
text_input.grid(row = 1, column = 0)

# For the system to see
image = Image.new("RGB", (640, 320), (255, 255, 255))
draw = ImageDraw.Draw(image)

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
    draw.line([old_x, old_y, x, y], (0, 0, 0))
    old_x = x
    old_y = y

def on_mouse_release(event):
    global old_x
    global old_y
    old_x = None
    old_y = None

def save_image(event):
    global text_input
    converted_name = convert_symbols(text_input.get()) + ".0"
    files = Path("./generated-data")
    highest_name = converted_name
    # Kind of messy
    for file in files.iterdir():
        if len(file.name.split(".")) != 3: continue
        if file.name.split(".", 1)[0] == highest_name.split(".", 1)[0]:
            if int(file.name.split(".", 2)[1]) >= int(highest_name.split(".", 1)[1]):
                highest_name = file.name.split(".", 1)[0] + "." + str(int(file.name.rsplit(".", 2)[1]) + 1)
    image.save(f"./generated-data/{highest_name}.png")

def convert_symbols(text):
    assert_type(text, str)
    return (text.replace("/", "d")
            .replace("+", "a")
            .replace("-", "s")
            .replace("*", "m")
            .replace("x", "m")
            )

canvas.bind("<B1-Motion>", on_mouse_move)
canvas.bind("<ButtonRelease-1>", on_mouse_release)
canvas.bind("<Button-3>", save_image)

button = tk.Button(root, text="Save")
button.bind("<Button-1>", save_image)
button.grid(row = 1, column = 1)

root.mainloop()