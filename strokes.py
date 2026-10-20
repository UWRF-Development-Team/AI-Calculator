from abc import ABC, abstractmethod

class CoordinatePair:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def as_list(self):
        return [self.x, self.y]

class Stroke(ABC):
    def __init__(self, start, end, color):
        self.start = start
        self.end = end
        self.color = color

    def draw(self, canvas, image):
        self.draw_canvas(canvas)
        self.draw_image(image)

    @abstractmethod
    def draw_canvas(self, canvas):
        pass

    @abstractmethod
    def draw_image(self, image):
        pass

class BrushStroke(Stroke):
    def __init__(self, start, end):
        super().__init__(start, end, "black")

    def draw_canvas(self, canvas):
        canvas.create_line(self.start.x, self.start.y, self.end.x, self.end.y, fill=self.color, width=3)

    def draw_image(self, image):
        image.line([self.start.x, self.start.y, self.end.x, self.end.y], (0, 0, 0), width=3)

class BoundingStroke(Stroke):
    def __init__(self, start, end):
        super().__init__(start, end, "red")

    def draw_canvas(self, canvas):
        canvas.create_rectangle(self.start.x, self.start.y, self.end.x, self.end.y, outline=self.color, width=3)

    def draw_image(self, image):
        pass

class StrokeCollection(Stroke):
    def __init__(self, strokes):
        super().__init__(None, None, None)
        self.strokes = strokes

    def draw_canvas(self, canvas):
        for stroke in self.strokes:
            stroke.draw_canvas(canvas)

    def draw_image(self, image):
        for stroke in self.strokes:
            stroke.draw_image(image)

    def push(self, stroke):
        self.strokes.append(stroke)

    def pop(self):
        return self.strokes.pop()