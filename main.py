import tkinter as tk
from typing import assert_type
from pathlib import Path
import json

from PIL import Image, ImageDraw

#Creating Window
root = tk.Tk()
root.minsize(640, 320)
root.title("AI Calculator")

#Equations / Answers Grid
eq_ans_frame = tk.Frame(root, bd=1, relief="solid")
eq_ans_frame.grid(row = 0, column = 0)

#Equations
equation1 = tk.Label(eq_ans_frame, text = "Equation 1")
equation1.grid(row = 0, column = 0)
equation2 = tk.Label(eq_ans_frame, text = "Equation 2")
equation2.grid(row = 1, column = 0)
equation3 = tk.Label(eq_ans_frame, text = "Equation 3")
equation3.grid(row = 2, column = 0)

#Answers
answer1 = tk.Label(eq_ans_frame, text = "Answer 1")
answer1.grid(row = 0, column = 1)
answer2 = tk.Label(eq_ans_frame, text = "Answer 2")
answer2.grid(row = 1, column = 1)
answer3 = tk.Label(eq_ans_frame, text = "Answer 3")
answer3.grid(row = 2, column = 1)

# Drawing Canvas
canvas = tk.Canvas(root, width=640, height=320)
canvas.grid(row = 2, column = 0)

#Text Input for saving canvas
text_input = tk.Entry(root)
text_input.grid(row = 3, column = 0, sticky = 's')

#Predicted Output From System
output = tk.Text(root, height=1, width=40)
output.grid(row = 1, column = 0)

predicted_input = "This is what the AI predicted." #Ideally, the AI would put it's guess in this varible

output.insert(tk.END, predicted_input)
output.config(state='disabled') #disabled/normal for post prediction edits


# For the system to see
image = Image.new("RGB", (640, 320), (255, 255, 255))
draw = ImageDraw.Draw(image)

old_x = None
old_y = None
bounds_x1 = None
bounds_y1 = None
strokes = [[]]
undid_strokes = []
bounds = []
undid_bounds = []
drawing = True

def draw_on_move(event):
    global old_x
    global old_y
    global undid_strokes
    undid_strokes = []
    x = event.x
    y = event.y
    old_x = x if old_x is None else old_x
    old_y = y if old_y is None else old_y
    strokes[-1].append([old_x, old_y, x, y])
    canvas.create_line(old_x, old_y, x, y, fill="black", width=3)
    draw.line([old_x, old_y, x, y], (0, 0, 0), width=3)
    old_x = x
    old_y = y

def stop_draw(event):
    global old_x
    global old_y
    old_x = None
    old_y = None
    strokes.append([])

def save_image(event):
    global text_input
    converted_name = convert_symbols(text_input.get()) + ".0"
    files = Path("training-data")
    highest_name = converted_name
    # Kind of messy
    for file in files.iterdir():
        if len(file.name.split(".")) != 3: continue
        if file.name.split(".", 1)[0] == highest_name.split(".", 1)[0]:
            if int(file.name.split(".", 2)[1]) >= int(highest_name.split(".", 1)[1]):
                highest_name = file.name.split(".", 1)[0] + "." + str(int(file.name.rsplit(".", 2)[1]) + 1)
    image.save(f"./training-data/{highest_name}.png")
    update_json(highest_name+".png", text_input.get())

def update_json(file_name, key):
    if len(key) != len(bounds): raise ValueError("key does not match bounds")
    training_json = json.load(open("./data.json"))

    save_bounds = []
    # Sorts by the first element in each list in ascending order, exactly what we want!
    for i, bound in enumerate(sorted(bounds)):
        bound_dict = {
            "character": key[i],
            "start": [bound[0], bound[1]],
            "end": [bound[2], bound[3]],
        }
        save_bounds.append(bound_dict)

    image_data = {
        "filename": file_name,
        "bounds": save_bounds
    }

    training_json.append(image_data)
    json.dump(training_json, open("./data.json", "w"))

def convert_symbols(text):
    assert_type(text, str)
    return (text.replace("/", "d")
            .replace("+", "a")
            .replace("-", "s")
            .replace("*", "m")
            .replace("x", "m")
            )

def clear_canvas(event):
    global image, draw, text_input, strokes, undid_strokes, bounds, undid_bounds, drawing
    drawing = True
    bind_draw()
    image = Image.new("RGB", (640, 320), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    canvas.delete("all")
    text_input.delete(0, tk.END)
    strokes = [[]]
    undid_strokes = []
    bounds = []
    undid_bounds = []

def draw_undo(event):
    global image
    global draw
    global text_input
    if len(strokes[-1]) == 0:
        if len(strokes) > 1:
            strokes.pop()
        else:
            return
    undid_strokes.append(strokes.pop())
    image = Image.new("RGB", (640, 320), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    canvas.delete("all")
    for stroke in strokes:
        for strokePart in stroke:
            canvas.create_line(strokePart[0], strokePart[1], strokePart[2], strokePart[3], fill="black", width=3)
            draw.line(strokePart, (0, 0, 0), width=3)

    strokes.append([])

def draw_redo(event):
    if len(undid_strokes) == 0:
        return
    redo_stroke = undid_strokes.pop()
    for strokePart in redo_stroke:
        canvas.create_line(strokePart[0], strokePart[1], strokePart[2], strokePart[3], fill="black", width=3)
        draw.line(strokePart, (0, 0, 0), width=3)
    strokes[-1] = redo_stroke
    strokes.append([])

def bounds_start(event):
    global bounds_x1
    global bounds_y1
    bounds_x1 = event.x
    bounds_y1 = event.y

def bounds_rectangle(event):
    canvas.create_rectangle(bounds_x1, bounds_y1, event.x, event.y, outline="#ff0000", width=3)
    bounds.append([bounds_x1, bounds_y1, event.x, event.y])

def bounds_undo(event):
    if len(bounds) < 1: return
    undid_rectangle = bounds.pop()
    undid_bounds.append(undid_rectangle)

    # have to redo EVERYTHING
    canvas.delete("all")
    for stroke in strokes:
        for strokePart in stroke:
            canvas.create_line(strokePart[0], strokePart[1], strokePart[2], strokePart[3], fill="black", width=3)

    for box in bounds:
        canvas.create_rectangle(box[0], box[1], box[2], box[3], outline="#ff0000", width=3)

def bounds_redo(event):
    if len(undid_bounds) < 1: return
    redid_rectangle = undid_bounds.pop()
    bounds.append(redid_rectangle)

    canvas.create_rectangle(redid_rectangle[0], redid_rectangle[1], redid_rectangle[2], redid_rectangle[3], outline="#ff0000", width=3)


def bind_draw():
    global drawing
    drawing = True
    canvas.bind("<B1-Motion>", draw_on_move)
    canvas.bind("<ButtonRelease-1>", stop_draw)
    root.bind("<Control-z>", draw_undo)
    root.bind("<Control-y>", draw_redo)
    redo_button.bind("<Button-1>", draw_redo)
    undo_button.bind("<Button-1>", draw_undo)

def bind_boxes():
    global drawing
    drawing = False
    canvas.unbind("<B1-Motion>")
    canvas.bind("<Button-1>", bounds_start)
    canvas.bind("<ButtonRelease-1>", bounds_rectangle)
    root.bind("<Control-z>", bounds_undo)
    root.bind("<Control-y>", bounds_redo)
    redo_button.bind("<Button-1>", bounds_redo)
    undo_button.bind("<Button-1>", bounds_undo)

def toggle_mode(event):
    if drawing:
        bind_boxes()
    else:
        bind_draw()

#Keybindings

root.bind("<Control-q>", toggle_mode)

#Seperate frame needed to display buttons correctly
clear_save_frame = tk.Frame(root)
clear_save_frame.grid(row = 3, column = 0, sticky = 'es')

save_button = tk.Button(clear_save_frame, text="Save")
save_button.bind("<Button-1>", save_image)
save_button.grid(row = 0, column = 0)

clear_button = tk.Button(clear_save_frame, text="Clear")
clear_button.bind("<Button-1>", clear_canvas)
clear_button.grid(row = 0, column = 1)

#Seperate frame needed to display buttons correctly
undo_redo_frame = tk.Frame(root)
undo_redo_frame.grid(row = 3, column = 0, sticky="ws")

undo_button = tk.Button(undo_redo_frame, text="Undo")
undo_button.grid(row = 0, column = 0)

redo_button = tk.Button(undo_redo_frame, text="Redo")
redo_button.grid(row = 0, column = 1)

bind_draw()

root.mainloop()