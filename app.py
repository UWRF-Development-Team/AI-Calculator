import tkinter as tk
from tkinter import TclError, ttk
from typing import assert_type 
from pathlib import Path
from PIL import Image, ImageDraw


# Display Frame
class DisplayFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        
        self.eq1 = tk.Label(self, text = "Equation 1")
        self.eq1.grid(column = 0, row = 0)
    
# Canvas Frame
class CanvasFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.old_x = None
        self.old_y = None
        self.strokes = [[]]
        self.undid_strokes = []

        self.canvas = tk.Canvas(self, bg="red")
        self.canvas.pack(fill = "both", expand = 1)

        self.image = Image.new("RGB", (container.window_width, container.window_height), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)

        self.canvas.bind("<B1-Motion>", self.on_mouse_pressed)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_released)
        

    def on_mouse_pressed(self, event):
        self.undid_strokes = []
        x = event.x
        y = event.y
        self.old_x = x if self.old_x is None else self.old_x
        self.old_y = y if self.old_y is None else self.old_y
        self.strokes[-1].append([self.old_x, self.old_y, x, y])
        self.canvas.create_line(self.old_x, self.old_y, x, y, fill = "black", width = 3)
        self.draw.line([self.old_x, self.old_y, x, y], (0, 0, 0), width = 3)
        self.old_x = x
        self.old_y = y

    def on_mouse_released(self, event):
        self.old_x = None
        self.old_y = None
        self.strokes.append([])

    def redo(self):
        return

    def undo(self):
        return

    def clear(self, container):
        self.image = Image.new("RGB", (container.window_width, container.window_height), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        self.canvas.delete("all")
        self.strokes = [[]]
        self.undid_strokes = []
        
    def save(self, file_name):
        return

# Bottom Toolbar Frame
class ToolbarFrame(ttk.Frame):
    def __init__(self, container, canvas):
        super().__init__(container)
        
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 3)
        self.columnconfigure(3, weight = 1)
        self.columnconfigure(4, weight = 1)
        self.rowconfigure(0, weight = 1)

        undo_button = ttk.Button(self, text = "undo", command = canvas.undo)
        undo_button.grid(column = 0, row = 0, sticky="SW", padx = 5, pady = 5)

        redo_button = ttk.Button(self, text = "redo", command = canvas.redo)
        redo_button.grid(column = 1, row = 0, sticky="SW", padx = 5, pady = 5)
        
        file_name = ttk.Entry(self)
        file_name.grid(column = 2, row = 0, sticky="S", padx = 5, pady = 5)
        
        clear_button = ttk.Button(self, text = "clear", command = canvas.clear(container))
        clear_button.grid(column = 3, row = 0, sticky="SE", padx = 5, pady = 5)
        
        save_button = ttk.Button(self, text = "save", command = canvas.save(file_name.get()))
        save_button.grid(column = 4, row = 0, sticky="SE", padx = 5, pady = 5)
        



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Calc, calc is short for calculator btw chat, just using slang, incase youre new to the stream")
    
        self.window_height = 600
        self.window_width  = 800
        screen_height = self.winfo_screenheight()
        screen_width  = self.winfo_screenwidth()
        center_x = int(screen_width / 2 - self.window_width / 2)
        center_y = int(screen_height / 2 - self.window_height / 2)

        self.geometry(f'{self.window_width}x{self.window_height}+{center_x}+{center_y}')
        self.resizable(0, 0)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 3, uniform = "rows")
        self.rowconfigure(1, weight = 1, uniform = "rows")
        self.rowconfigure(2, weight = 6, uniform = "rows")
        self.rowconfigure(3, weight = 2, uniform = "rows")

        self.__create_frames()
    
    def __create_frames(self):
        display_frame = DisplayFrame(self)
        display_frame.grid(column = 0, row = 0, sticky="NEW")

        canvas_frame = CanvasFrame(self)
        canvas_frame.grid(column = 0, row = 2, sticky="NESW")

        toolbar_frame = ToolbarFrame(self, canvas_frame)
        toolbar_frame.grid(column = 0, row = 3, sticky="SEW")



if __name__ == "__main__":
    app = App()
    app.mainloop()
