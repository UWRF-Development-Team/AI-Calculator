from strokes import *

class History:
    def __init__(self, canvas, image):
        self.canvas = canvas
        # ImageDraw from PIL, not Image
        self.image = image
        self.main_history = StrokeCollection()
        self.undo_history = StrokeCollection()

    def redraw(self):
        # Fill area with white
        self.image.rectangle([-1, -1, 1000, 1000], fill="white")
        self.canvas.delete("all")
        self.main_history.draw(self.canvas, self.image)

    def redraw_canvas(self):
        self.canvas.delete("all")
        self.main_history.draw_canvas(self.canvas)

    def redraw_image(self):
        # Fill area with white
        self.image.rectangle(-1, -1, 1000, 1000, fill="white")
        self.main_history.draw_image(self.image)

    def undo(self):
        if self.main_history.is_empty():
            raise LookupError("Can't undo, no strokes exist")

        self.undo_history.push(self.main_history.pop())
        self.redraw()

    def redo(self):
        if self.undo_history.is_empty():
            raise LookupError("Can't redo, no strokes exist")

        self.main_history.push(self.undo_history.pop())
        self.redraw()

    def add_stroke(self, stroke):
        self.main_history.push(stroke)
        self.undo_history = StrokeCollection()

    def reset(self):
        self.main_history = StrokeCollection()
        self.undo_history = StrokeCollection()
        self.redraw()