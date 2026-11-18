import tkinter as tk
import numpy as np
from tkinter import ttk, messagebox
from typing import assert_type 
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from keras.utils import img_to_array
import json
from matplotlib import pyplot as plt
import cv2

from equation_history import EquationHistory
from history import *
from themes import THEMES
from models import *

classifier = Classifier()
detector = Detector()

# Tab Frame
class TabsFrame(ttk.Frame):
    def __init__(self, container):
            super().__init__(container)
            self.notebook = ttk.Notebook(self)
            self.notebook.pack(fill="both", expand=True)

            self.tab1 = ttk.Frame(self.notebook)
            self.tab2 = ttk.Frame(self.notebook)
            self.tab3 = ttk.Frame(self.notebook)

            self.notebook.add(self.tab1, text="Calculator")
            self.notebook.add(self.tab2, text="History")
            self.notebook.add(self.tab3, text="Settings")

# Display Frame
class HistoryFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self["relief"] = "solid"
        self["borderwidth"] = 2
        self["padding"] = 10

        #Setting Rows and Columns size/style
        self.columnconfigure(0, weight = 0)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.columnconfigure(3, weight = 0)
        self.rowconfigure(0, weight = 1, uniform = "rows")
        self.rowconfigure(1, weight = 1, uniform = "rows")
        self.rowconfigure(2, weight = 1, uniform = "rows")
        self.rowconfigure(3, weight = 1, uniform = "rows")

        #Equation History
        self.equation_history = EquationHistory(self, 3)

        #AI Output Row
        self.output = tk.Text(self, height = 1, width = 40)
        self.output.grid(row = 3)
        self.output.insert(index = 1.0, chars = "AI OUTPUT")
        self.output.config(state = "disabled")
        self.output.grid(column = 1, row = 3, columnspan = 2, sticky ="EW")

class ExtendedHistoryFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self["relief"] = "solid"
        self["borderwidth"] = 2
        self["padding"] = 10

        self.equation_history = EquationHistory(self, 10)

# Canvas Frame
class CanvasFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        # self['padding'] = 5
        # self['bg'] = canvas_color
        # self.padding = 5
        # self.background = canvas_color

        # Object variables to store persistent state
        # First three are used to track brush strokes between each mouse move call
        self.old_x = None
        self.old_y = None
        self.current_stroke = []
        self.drawing = True
        self.calc_mode = True
        self.draw_type = BrushStroke
        self.previous_bounds = None # For bounding box

        self.history_changed = None

        # Create and set up Canvas, Image, and ImageDraw
        self.canvas = tk.Canvas(self,bg=THEMES["Light"].canvas,highlightthickness=5,highlightbackground=THEMES["Light"].border,width=640,height=320)
        self.canvas = tk.Canvas(self,bg=THEMES["Light"].canvas,highlightthickness=5,highlightbackground=THEMES["Light"].border,width=640,height=320)

        self.canvas.grid(row = 2, column = 0)

        self.image = Image.new("L", (640, 320), 255)
        self.draw = ImageDraw.Draw(self.image)

        # Initialize history
        self.history = History(self.canvas, self.draw)

        # Keybinds
        self.canvas.bind("<B1-Motion>", self.on_mouse_pressed)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_released)
        self.winfo_toplevel().bind("<Control-z>", self.undo)
        self.winfo_toplevel().bind("<Control-y>", self.redo)
        self.winfo_toplevel().bind("<Control-q>", self.toggle)
        self.canvas.bind("<Configure>", self.on_resize)
        self.winfo_toplevel().bind("<Control-e>", self.toggle_eraser)

    # tells toolbar to update buttons
    def signal_toolbar(self):
        if self.history_changed:
            self.history_changed()

    def toggle(self, event=None):
        if self.calc_mode: return
        self.drawing = not self.drawing

    # Drawing
    def on_mouse_pressed(self, event):
        x = event.x
        y = event.y

        # Check if this is the first movement of a new stroke (collection)
        if self.old_x is None:
            # Just draw in the same place this time
            self.old_x = x
            self.old_y = y
            # self.current_stroke is unused for bounding
            # Use it to store the starting coordinates instead
            if not self.drawing:
                self.current_stroke.append([x, y])

        end = CoordinatePair(x, y)
        if self.drawing:
            start = CoordinatePair(self.old_x, self.old_y)
            # Can be either a dark line (Brush) or white line (Eraser)
            stroke = self.draw_type(start, end)
            stroke.draw(self.canvas, self.draw)
            self.current_stroke.append(stroke)
        else:
            # Use starting coordinates, not previous ones
            start = CoordinatePair(self.current_stroke[0][0], self.current_stroke[0][1])
            # Remove previous bound if it exists, cheaper than redrawing
            if self.previous_bounds is not None:
                self.previous_bounds.remove_canvas(self.canvas)

            # Create, save, and draw new bounding box
            stroke = BoundingStroke(start, end)
            self.previous_bounds = stroke
            stroke.draw(self.canvas, self.draw)

        # Reset old variables
        self.old_x = x
        self.old_y = y

    # Stops drawing
    def on_mouse_released(self, event):
        if self.current_stroke is None or not self.current_stroke: return # If mouse didn't move, return
        # Don't draw in this method because it was done in the last on_mouse_pressed() call
        if self.drawing:
            # Create new stroke collection and save it
            self.history.add_stroke(StrokeCollection(self.current_stroke))
        else:
            start = CoordinatePair(self.current_stroke[0][0], self.current_stroke[0][1])
            end = CoordinatePair(event.x, event.y)
            # Save in history, unlike when moving
            new_stroke = BoundingStroke(start, end)
            new_stroke.draw(self.canvas, self.image)
            if self.previous_bounds: self.previous_bounds.remove_canvas(self.canvas)
            self.history.add_stroke(new_stroke)
            self.previous_bounds = None

        self.signal_toolbar()

        # Reset some states
        self.current_stroke = []

        self.old_x = None
        self.old_y = None


    def redo(self, event=None):
        self.history.redo()
        self.signal_toolbar()

    def undo(self, event=None):
        self.history.undo()
        self.signal_toolbar()

    def clear(self, event=None):
        self.drawing = True
        self.history.reset()
        self.signal_toolbar()

    def convert_symbols(self, text):
        assert_type(text, str)
        return (text.replace("/", "d")
             .replace("+", "a")
             .replace("-", "s")
             .replace("*", "m")
             .replace("x", "m")
        )

    def save(self, file_name):
        # If the file name was forgotten
        if len(file_name) == 0:
            messagebox.showerror(title = "Save Error", message = "Need a file name!")
            return
        # If no image was drawn
        if self.history.main_history.is_empty():
            messagebox.showerror(title = "Save Error", message = "Cannot save an empty file!")
            return
        # If the number of bounds does not match the number of glyphs in the target
        bounds = self.history.main_history.get_strokes_of_type(BoundingStroke)
        if len(file_name) != bounds.length():
            messagebox.showerror(title="Save Error", message="Key does not match bounds!")
            return

        # Parse name to remove special characters
        converted_name = self.convert_symbols(file_name) + ".0"
        files = Path("./training-data/images")
        # If directory is missing, make it
        if not files.is_dir():
            files.mkdir(parents=True)

        # We should probably rewrite this
        # Renames the file to avoid file collisions by incrementing the .n part of the filename
        highest_name = converted_name
        for file in files.iterdir():
            if len(file.name.split(".")) != 3: continue
            if file.name.split(".", 1)[0] == highest_name.split(".", 1)[0]:
                if int(file.name.split(".", 2)[1]) >= int(highest_name.split(".", 1)[1]):
                    highest_name = file.name.split(".", 1)[0] + "." + str(int(file.name.rsplit(".", 2)[1]) + 1)

        self.image.save(f"{str(files)}/{highest_name}.png")
        self.update_json(highest_name + ".png", file_name, bounds)

    def update_json(self, file_name, key, bounds):
        # Double check that the target and boxes have the same number of features
        if len(key) != bounds.length(): raise ValueError("key does not match bounds")

        # Create empty JSON array if the file does not exist
        if not Path("./training-data/data.json").is_file():
            json.dump([], open("./training-data/data.json", "x"))
        training_json = json.load(open("./training-data/data.json"))

        save_bounds = []
        # Sort bounds left to right
        bounds.sort()
        # Generate an object for each bound
        for i, bound in enumerate(bounds.as_list()):
            bound_dict = {
                "character": key[i],
                "start": bound.start.as_list(),
                "end": bound.end.as_list(),
            }
            save_bounds.append(bound_dict)

        # Save file name (key) and bounds data (value)
        image_data = {
            "filename": file_name,
            "bounds": save_bounds
        }

        # Append to array
        training_json.append(image_data)
        json.dump(training_json, open("./training-data/data.json", "w"), indent=2)

    def on_resize(self, event):
        self.history.redraw()

    def toggle_mode(self):
        self.calc_mode = not self.calc_mode

    def toggle_eraser(self, event=None):
        if self.draw_type == BrushStroke:
            self.draw_type = EraserStroke
        else:
            self.draw_type = BrushStroke

# Bottom Toolbar Frame
class ToolbarFrame(ttk.Frame):
    def __init__(self, container, canvas, display):
        super().__init__(container)

        self.canvas = canvas
        self.display = display

        self.calc_mode = True

        self.configure(style="My.TFrame")

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 3)
        self.columnconfigure(3, weight = 1)
        self.columnconfigure(4, weight = 1)
        self.rowconfigure(0, weight = 1)

        self.undo_button = ttk.Button(self, text = "Undo", command = canvas.undo)
        self.undo_button.grid(column = 0, row = 0, sticky="WS", padx = 5, pady = 5)

        self.redo_button = ttk.Button(self, text = "Redo", command = canvas.redo)
        self.redo_button.grid(column = 1, row = 0, sticky="WS", padx = 5, pady = 5)

        self.brush_button = ttk.Button(self, text="Brush", command=canvas.toggle_eraser)
        self.brush_button.grid(column=2, row=0, padx=5, pady=5)

        # Not displayed by default
        self.file_name = ttk.Entry(self)
        self.toggle_button = ttk.Button(self, text="Toggle", command=canvas.toggle)
        self.file_name.bind("<KeyRelease>", self.update_buttons)

        self.clear_button = ttk.Button(self, text = "Clear", command = self.clear)
        self.clear_button.grid(column = 5, row = 0, sticky="ES", padx = 5, pady = 5)
        
        self.save_button = ttk.Button(self, text = "Calc", command = self.submit)
        self.save_button.grid(column = 6, row = 0, sticky="ES", padx = 5, pady = 5)

    # disabled/enables toolbar buttons.
    def update_buttons(self, event=None):
        # Checks undos
        if self.canvas.history.main_history.is_empty():
            self.undo_button.state(["disabled"])
            self.save_button.state(["disabled"])
        else:
            self.undo_button.state(["!disabled"])
            self.save_button.state(["!disabled"])

        # Disable clear only if NOTHING has been done
        if self.canvas.history.main_history.is_empty() and self.canvas.history.undo_history.is_empty():
            self.clear_button.state(["disabled"])
        else:
            self.clear_button.state(["!disabled"])

        # checks redos
        if self.canvas.history.undo_history.is_empty():
            self.redo_button.state(["disabled"])
        else:
            self.redo_button.state(["!disabled"])

        # checks if entry is empty only in training data mode
        if not self.calc_mode and self.file_name.get() == "":
            self.save_button.state(["disabled"])

        if len(list(self.file_name.get())) != self.canvas.history.main_history.get_strokes_of_type(BoundingStroke).length():
            self.save_button.state(["disabled"])


    def save(self):
        self.canvas.save(self.file_name.get())
        self.clear()

    def clear(self, event=None):
        self.canvas.clear()
        self.file_name.delete(0, tk.END)

    def submit(self, event=None):

        # self.display.add_equation(equation, answer)
        image_array = img_to_array(self.canvas.image.convert("L").resize((160, 80)))
        image_array = np.expand_dims(image_array, axis=0)
        _, thresh = cv2.threshold(np.array(self.canvas.image).copy(), 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        predicted_characters = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 5:
                x, y, w, h = cv2.boundingRect(cnt)
                proc = process_image(self.canvas.image, [x,y,x+w,y+h])
                BoundingStroke(CoordinatePair(x,y), CoordinatePair(x+w, y+h)).draw(self.canvas.canvas, self.canvas.image)
                arr = img_to_array(proc, dtype="float32")/255.0
                # TODO double double double check shape here, this might not actually be the right image portion
                # or even a meaningful image at all
                array = np.expand_dims(arr/255.0, axis=0)
                prediction = classifier.predict(array)
                predicted_characters.append(prediction)
                print(prediction)

        app.update_text("".join(predicted_characters))

    def toggle_mode(self):
        if self.calc_mode:
            self.toggle_button.grid(column=4, row=0, sticky="ES", padx=5, pady=5)
            self.file_name.grid(column = 3, row = 0, sticky="S", padx = 5, pady = 5)
            self.save_button.configure(text="Save", command=self.save)
        else:
            self.toggle_button.grid_forget()
            self.file_name.grid_forget()
            self.save_button.configure(text="Calc", command=self.submit)
        self.calc_mode = not self.calc_mode
        self.update_buttons()

class SettingsFrame(ttk.Frame):
    def __init__(self, container, app):
        super().__init__(container)
        self.app = app

        ttk.Label(self, text="Application Theme:").grid(row=0, column=0)
        ttk.Button(self,text="Switch Theme", command=self.app.toggle_theme).grid(row=0, column=1)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Calculator!")
        self.configure(padx=5, pady=5)

        self.current_theme = THEMES["Light"]
        self.style = ttk.Style(self)
    
        # self.window_height = 640
        # self.window_width  = 640
        # screen_height = self.winfo_screenheight()
        # screen_width  = self.winfo_screenwidth()
        # center_x = int(screen_width / 2 - self.window_width / 2)
        # center_y = int(screen_height / 2 - self.window_height / 2)
        # self.geometry(f'{self.window_width}x{self.window_height}+{center_x}+{center_y}')
        # self.minsize(640, 320)

        self.columnconfigure(0, weight = 1)
        # self.rowconfigure(0, weight = 3, uniform = "rows")
        # self.rowconfigure(1, weight = 0, uniform = "rows")
        self.rowconfigure(2, weight = 1,)
        # self.rowconfigure(3, weight = 1, uniform = "rows")

        self.__create_frames()
        # Uppercase T means shift-t, wow
        self.bind("<Control-T>", self.toggle_mode)

    def __create_frames(self):

        # Calculator Tab
        tabs_frame = TabsFrame(self)
        tabs_frame.grid(column=0, row=0)

        self.history_frame = HistoryFrame(tabs_frame.tab1)
        self.history_frame.grid(column = 0, row = 0, sticky="NEW")

        self.canvas_frame = CanvasFrame(tabs_frame.tab1)
        self.canvas_frame.grid(column = 0, row = 2)

        # History Tab
        self.extended_history_frame = ExtendedHistoryFrame(tabs_frame.tab2)
        self.extended_history_frame.grid(column = 0, row = 0, sticky="NEW")

        #Toolbar Frame
        self.toolbar_frame = ToolbarFrame(tabs_frame.tab1, self.canvas_frame, self.extended_history_frame)
        self.toolbar_frame.grid(column = 0, row = 3, sticky="SEW")


        # connects canvas's history changed var and toolbar's update buttons function, so you can call update buttons from canvas frame
        self.canvas_frame.history_changed = self.toolbar_frame.update_buttons
        # initial update
        self.toolbar_frame.update_buttons()

        #Settings Tab
        self.settings_frame = SettingsFrame(tabs_frame.tab3, self)
        self.settings_frame.grid(row=0, column=0, sticky="NW")

        self.apply_theme()

    def toggle_theme(self):
        if self.current_theme == THEMES["Light"]:
            self.current_theme = THEMES["Dark"]
        else:
            self.current_theme = THEMES["Light"]

        self.apply_theme()

    def apply_theme(self):
        theme = self.current_theme

        self.configure(bg=theme.background)

        self.style.configure("TFrame", background=theme.background)

        self.style.configure("TLabel", background=theme.background, foreground=theme.foreground)

        self.style.configure("TNotebook", background=theme.background)

        self.style.map("TNotebook.Tab",background=[("selected", theme.accent)])

        self.style.configure("My.TFrame",background=theme.accent)

        self.canvas_frame.canvas.configure(bg=theme.canvas, highlightbackground=theme.border)


    def toggle_mode(self, event=None):
        self.toolbar_frame.toggle_mode()
        self.canvas_frame.toggle_mode()

    def update_text(self, equation):
        # todo send model code here
        self.extended_history_frame.equation_history.enqueue(equation)
        self.history_frame.equation_history.enqueue(equation)

if __name__ == "__main__":
    app = App()
    app.update_idletasks()
    app.minsize(app.winfo_width(), app.winfo_height())
    app.mainloop()
