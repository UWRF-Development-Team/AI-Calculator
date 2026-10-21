from strokes import *

# Contains drawing history and methods to slightly modify and restore the canvas/image
class History:
    # Takes a tkinter Canvas and PIL ImageDraw
    def __init__(self, canvas, image):
        self.canvas = canvas
        self.image = image
        # The stroke history of the user
        self.main_history = StrokeCollection()
        # The history of the undid strokes
        self.undo_history = StrokeCollection()

    # Reset canvas and image
    def redraw(self):
        # Fill area with white
        self.image.rectangle([-1, -1, 1000, 1000], fill="white")
        self.canvas.delete("all")
        self.main_history.draw(self.canvas, self.image)

    # Reset canvas
    def redraw_canvas(self):
        self.canvas.delete("all")
        self.main_history.draw_canvas(self.canvas)

    # Reset image
    def redraw_image(self):
        # Fill area with white
        self.image.rectangle(-1, -1, 1000, 1000, fill="white")
        self.main_history.draw_image(self.image)

    def undo(self):
        # Returns, but could throw an error or do some kind of warning
        if self.main_history.is_empty():
            return

        # Move the last entry from the main history to the undo history
        self.undo_history.push(self.main_history.pop())
        # Redrawing is much easier than erasing
        self.redraw()

    def redo(self):
        if self.undo_history.is_empty():
            return

        self.main_history.push(self.undo_history.pop())
        # Could just draw the last stroke, but done this way for parity
        self.redraw()

    # Save a stroke to the history, but does not draw it
    def add_stroke(self, stroke):
        self.main_history.push(stroke)
        self.undo_history = StrokeCollection()

    # Reset history, and clears the canvas and image
    def reset(self):
        self.main_history = StrokeCollection()
        self.undo_history = StrokeCollection()
        self.redraw()