from tkinter.ttk import Label, Button


class EquationHistory:
    def __init__(self, frame, amount):
        self.frame = frame
        pass

    def enqueue(self, equation_string):
        pass

    def extend(self):
        pass

class EquationElement:
    def __init__(self, frame, num):
        self.answer = Label(frame, text="")
        self.equation = Label(frame, text="")
        self.copy_answer = Button(frame, text="Copy",
            command=lambda: copy(frame, self.answer["text"]))
        self.copy_equation = Button(frame, text="Copy",
            command=lambda: copy(frame, self.equation["text"]))

        self.answer.grid(column=2, row=num, sticky="E")
        self.equation.grid(column=1, row=num, sticky="W")
        self.copy_answer.grid(column=3, row=num, sticky="E")
        self.copy_equation.grid(column=0, row=num, sticky="W")


    def update(self, equation_string):
        self.equation["text"] = equation_string
        self.answer["text"] = eval(equation_string) # Technically bad

def copy(frame, answer):
    frame.clipboard_clear()
    frame.clipboard_append(answer)