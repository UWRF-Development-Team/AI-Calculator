from tkinter.ttk import Label, Button

class EquationHistory:
    def __init__(self, frame, amount):
        self.frame = frame
        self.queue = []

        for i in range(amount):
            self.queue.append(EquationElement(frame, i))

    def enqueue(self, equation_string):
        last_equation = equation_string
        for element in self.queue:
            temp = element.equation
            element.update(last_equation)
            last_equation = temp

    def extend(self):
        self.queue.append(EquationElement(self.frame, len(self.queue)-1))

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