class Transformation:

    def __init__(self, oper, a, b):
        self.oper = oper
        self.a = a
        self.b = b
        self.result = None

        self.before = None
        self.after = None
        self.delta = None
        self.perc_delta = None

        if hasattr(b, "name"):
            self.name = b.name
        else:
            self.name = "CONST"

        self.calculate()

    def __repr__(self):
        return "Transformation({},{},{})".format(self.oper, self.a, self.b)

    def line_summary(self):
        return "{}".format(self.result)

    def calculate(self):
        self.before = self.a
        self.after = self.oper(self.a, self.b)
        self.result = self.after
        self.delta = self.after - self.before
        if self.a != 0:
            self.perc_delta = self.delta / self.a
        else:
            self.perc_delta = 1
