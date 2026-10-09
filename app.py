import tkinter as tk
from tkinter import TclError, ttk, messagebox
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

        self.canvas = tk.Canvas(self, bg="red", highlightthickness = 0)
        self.canvas.pack(fill = "both", expand = 1)

        self.image = Image.new("RGB", (1, 1), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)

        # keybinds
        self.canvas.bind("<B1-Motion>", self.on_mouse_pressed)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_released)
        self.winfo_toplevel().bind("<Control-z>", self.undo)
        self.winfo_toplevel().bind("<Control-y>", self.redo)
        self.canvas.bind("<Configure>", self.on_resize)

    # Drawing
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

    # Stops drawing
    def on_mouse_released(self, event):
        self.old_x = None
        self.old_y = None
        self.strokes.append([])

    def redo(self, event = None): 
        if len(self.undid_strokes) == 0:
            return
        redo_stroke = self.undid_strokes.pop()
        for line in redo_stroke:
            self.canvas.create_line(line[0], line[1], line[2], line[3], fill = "black", width = 3)
            self.draw.line(line, (0, 0, 0), width = 3)
        self.strokes[-1] = redo_stroke
        self.strokes.append([])

    def undo(self, event = None):
        if len(self.strokes[-1]) == 0:
            if len(self.strokes) > 0:
                self.strokes.pop()
            else:
                return

        self.undid_strokes.append(self.strokes.pop())
        self.image = Image.new("RGB", self.image.size, (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        self.canvas.delete("all")
        
        for stroke in self.strokes:
            for line in stroke:
                self.canvas.create_line(line[0], line[1], line[2], line[3], fill = "black", width = 3)
                self.draw.line(line, (0, 0, 0), width = 3)

        self.strokes.append([])

    def clear(self):
        self.image = Image.new("RGB", self.image.size, (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        self.canvas.delete("all")
        self.strokes = [[]]
        self.undid_strokes = []
        
    def convert_symbols(self, text):
        assert_type(text, str)
        return (text.replace("/", "d")
             .replace("+", "a")
             .replace("-", "s")
             .replace("*", "m")
             .replace("x", "m")
        )

    def save(self, file_name):
        if len(file_name) == 0:
            messagebox.showerror(title = "Save Error", message = "Need file name")
            return 
        if len(self.strokes[0]) == 0:
            messagebox.showerror(title = "Save Error", message = "Cannot save empty file")
            return

        converted_name = self.convert_symbols(file_name) + ".0"
        files = Path("training-data")
        highest_name = converted_name
        for file in files.iterdir():
            if len(file.name.split(".")) != 3: continue
            if file.name.split(".", 1)[0] == highest_name.split(".", 1)[0]:
                if int(file.name.split(".", 2)[1]) >= int(highest_name.split(".", 1)[1]):
                    highest_name = file.name.split(".", 1)[0] + "." + str(int(file.name.rsplit(".", 2)[1]) + 1)
        self.image.save(f"./training-data/{highest_name}.png")

    def on_resize(self, event):
        self.image = Image.new("RGB", (event.width, event.height), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)
        for stroke in self.strokes:
            for line in stroke:
                self.draw.line(line, (0, 0, 0), width = 3)


# Bottom Toolbar Frame
class ToolbarFrame(ttk.Frame):
    def __init__(self, container, canvas):
        super().__init__(container)
        self.canvas = canvas

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
        
        self.file_name = ttk.Entry(self)
        self.file_name.grid(column = 2, row = 0, sticky="S", padx = 5, pady = 5)
        
        clear_button = ttk.Button(self, text = "clear", command = canvas.clear)
        clear_button.grid(column = 3, row = 0, sticky="SE", padx = 5, pady = 5)
        
        save_button = ttk.Button(self, text = "save", command = self.save)
        save_button.grid(column = 4, row = 0, sticky="SE", padx = 5, pady = 5)
        
    def save(self):
        self.canvas.save(self.file_name.get())

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Calc. Calc is short for calculator btw chat just using slang incase youre new to the stream")
    
        self.window_height = 640
        self.window_width  = 640
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
        self.rowconfigure(3, weight = 1, uniform = "rows")

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
