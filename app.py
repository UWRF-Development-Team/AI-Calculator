import tkinter as tk
from tkinter import ttk, messagebox
from typing import assert_type 
from pathlib import Path
from PIL import Image, ImageDraw
import json

from history import *

background_color = "#E1E2E4"
canvas_color = "#F8F9FA"
accent_color_light = "#ad1233"
accent_color_dark = "#696E71"

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
class DisplayFrame(ttk.Frame):
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

        #Equation and Answer Text
        self.eq1 = ttk.Label(self, text = "Equation 1")
        self.eq2 = ttk.Label(self, text = "Equation 2")
        self.eq3 = ttk.Label(self, text = "Equation 3")
        self.a1 = ttk.Label(self, text = "Answer 1")
        self.a2 = ttk.Label(self, text = "Answer 2")
        self.a3 = ttk.Label(self, text = "Answer 3")

        #Copy Buttons
        self.copya1 = ttk.Button(self, text="Copy", command=lambda : DisplayFrame.copy(self, self.a1["text"]))
        self.copya2 = ttk.Button(self, text="Copy", command=lambda : DisplayFrame.copy(self, self.a2["text"]))
        self.copya3 = ttk.Button(self, text="Copy", command=lambda : DisplayFrame.copy(self, self.a3["text"]))
        self.copyeq1 = ttk.Button(self, text="Copy", command=lambda : DisplayFrame.copy(self, self.eq1["text"]))
        self.copyeq2 = ttk.Button(self, text="Copy", command=lambda : DisplayFrame.copy(self, self.eq2["text"]))
        self.copyeq3 = ttk.Button(self, text="Copy", command=lambda : DisplayFrame.copy(self, self.eq3["text"]))

        #AI Output Row
        self.output = tk.Text (self, height = 1, width = 40)
        self.output.grid(row = 3)
        self.output.insert(index = 1.0, chars = "AI OUTPUT")
        self.output.config(state = "disabled")

        #Setting elements into cells
        self.copyeq1.grid(column = 0, row = 0, sticky = "W")
        self.copyeq2.grid(column = 0, row = 1, sticky = "W")
        self.copyeq3.grid(column = 0, row = 2, sticky = "W")
        self.eq1.grid(column = 1, row = 0, sticky = "W")
        self.eq2.grid(column = 1, row = 1, sticky = "W")
        self.eq3.grid(column = 1, row = 2, sticky = "W")
        self.a1.grid(column = 2, row = 0, sticky = "E")
        self.a2.grid(column = 2, row = 1, sticky = "E")
        self.a3.grid(column = 2, row = 2, sticky = "E")
        self.copya1.grid(column = 3, row = 0, sticky = "E")
        self.copya2.grid(column = 3, row = 1, sticky = "E")
        self.copya3.grid(column = 3, row = 2, sticky = "E")
        self.output.grid(column = 1, row = 3, columnspan = 2, sticky ="EW")

    def copy(self, answer):
        self.clipboard_clear()
        self.clipboard_append(answer)


class DisplayFrameExtended(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        
        self["relief"] = "solid"
        self["borderwidth"] = 2

        self.stored_equations = []


        self.columnconfigure(0, weight = 3)
        self.columnconfigure(1, weight = 1)
        self.rowconfigure(0, weight = 1, uniform = "rows")
        self.rowconfigure(1, weight = 1, uniform = "rows")
        self.rowconfigure(2, weight = 1, uniform = "rows")

        self.eq1 = ttk.Label(self, text = "Equation 1")
        self.eq2 = ttk.Label(self, text = "Equation 2")
        self.eq3 = ttk.Label(self, text = "Equation 3")
        self.a1 = ttk.Label(self, text = "Answer 1")
        self.a2 = ttk.Label(self, text = "Answer 2")
        self.a3 = ttk.Label(self, text = "Answer 3")

        self.eq1.grid(column = 0, row = 0, sticky = "W")
        self.eq2.grid(column = 0, row = 1, sticky = "W")
        self.eq3.grid(column = 0, row = 2, sticky = "W")
        self.a1.grid(column = 1, row = 0, sticky = "E")
        self.a2.grid(column = 1, row = 1, sticky = "E")
        self.a3.grid(column = 1, row = 2, sticky = "E")        

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

        # Create and set up Canvas, Image, and ImageDraw
        self.canvas = tk.Canvas(self, bg=canvas_color, highlightthickness = 0, width=640, height=320)
        self.canvas = tk.Canvas(self, bg=canvas_color, highlightthickness = 5, highlightbackground=accent_color_dark, width=640, height=320)
        self.canvas.grid(row = 2, column = 0)

        self.image = Image.new("RGB", (640, 320), (255, 255, 255))
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
            stroke = BrushStroke(start, end)
            stroke.draw(self.canvas, self.draw)
            self.current_stroke.append(stroke)
        else:
            # Use starting coordinates, not previous ones
            start = CoordinatePair(self.current_stroke[0][0], self.current_stroke[0][1])
            # Redraw without saving history for moving box effect
            self.history.redraw()
            stroke = BoundingStroke(start, end)
            stroke.draw(self.canvas, self.draw)

        # Reset old variables
        self.old_x = x
        self.old_y = y

    # Stops drawing
    def on_mouse_released(self, event):
        # Don't draw in this method because it was done in the last on_mouse_pressed() call
        if self.drawing:
            # Create new stroke collection and save it
            self.history.add_stroke(StrokeCollection(self.current_stroke))
        else:
            start = CoordinatePair(self.current_stroke[0][0], self.current_stroke[0][1])
            end = CoordinatePair(event.x, event.y)
            # Save in history, unlike when moving
            self.history.add_stroke(BoundingStroke(start, end))

        # Reset some states
        self.current_stroke = []

        self.old_x = None
        self.old_y = None


    def redo(self, event=None):
        self.history.redo()

    def undo(self, event=None):
        self.history.undo()

    def clear(self, event=None):
        self.drawing = True
        self.history.reset()
    
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

        self.image.save(f"./training-data/{highest_name}.png")
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

# Bottom Toolbar Frame
class ToolbarFrame(ttk.Frame):
    def __init__(self, container, canvas):
        super().__init__(container)
        self.canvas = canvas

        self.calc_mode = True

        ttk.Style().configure("My.TFrame", background=accent_color_light)
        self.configure(style="My.TFrame")

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 3)
        self.columnconfigure(3, weight = 1)
        self.columnconfigure(4, weight = 1)
        self.rowconfigure(0, weight = 1)

        undo_button = ttk.Button(self, text = "Undo", command = canvas.undo)
        undo_button.grid(column = 0, row = 0, sticky="WS", padx = 5, pady = 5)

        redo_button = ttk.Button(self, text = "Redo", command = canvas.redo)
        redo_button.grid(column = 1, row = 0, sticky="WS", padx = 5, pady = 5)

        # Not displayed by default
        self.file_name = ttk.Entry(self)
        self.toggle_button = ttk.Button(self, text="Toggle", command=canvas.toggle)

        clear_button = ttk.Button(self, text = "Clear", command = self.clear)
        clear_button.grid(column = 4, row = 0, sticky="ES", padx = 5, pady = 5)
        
        self.save_button = ttk.Button(self, text = "Submit", command = self.submit)
        self.save_button.grid(column = 5, row = 0, sticky="ES", padx = 5, pady = 5)
        
    def save(self):
        self.canvas.save(self.file_name.get())

    def clear(self, event=None):
        self.canvas.clear()
        self.file_name.delete(0, tk.END)

    def submit(self, event=None):
        # TODO send information to model
        pass

    def toggle_mode(self):
        if self.calc_mode:
            self.toggle_button.grid(column=3, row=0, sticky="ES", padx=5, pady=5)
            self.file_name.grid(column = 2, row = 0, sticky="S", padx = 5, pady = 5)
            self.save_button.configure(text="Save", command=self.save)
        else:
            self.toggle_button.grid_forget()
            self.file_name.grid_forget()
            self.save_button.configure(text="Submit", command=self.submit)
        self.calc_mode = not self.calc_mode

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Calculator!")
        self.configure(background=background_color, padx=5, pady=5)
    
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

        self.display_frame = DisplayFrame(tabs_frame.tab1)
        self.display_frame.grid(column = 0, row = 0, sticky="NEW")

        self.canvas_frame = CanvasFrame(tabs_frame.tab1)
        self.canvas_frame.grid(column = 0, row = 2)

        self.toolbar_frame = ToolbarFrame(tabs_frame.tab1, self.canvas_frame)
        self.toolbar_frame.grid(column = 0, row = 3, sticky="SEW")

    def toggle_mode(self, event=None):
        self.toolbar_frame.toggle_mode()
        self.canvas_frame.toggle_mode()

        # History Tab
        display_frame_extended = DisplayFrameExtended(tabs_frame.tab2)
        display_frame_extended.grid(column = 0, row = 0, sticky="NSEW")

        

        #Settings Tab



if __name__ == "__main__":
    app = App()
    app.update_idletasks()
    app.minsize(app.winfo_width(), app.winfo_height())
    app.mainloop()
