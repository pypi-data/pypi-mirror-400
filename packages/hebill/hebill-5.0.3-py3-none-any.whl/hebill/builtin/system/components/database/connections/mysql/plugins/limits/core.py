class Limits(dict):
    def __init__(self, start=None, quantity=None):
        dict().__init__(self)
        self.set(start or 0, quantity or 0)

    def set(self, start, quantity):
        self.start = start
        self.quantity = quantity

    @property
    def start(self): return self["start"]
    @start.setter
    def start(self, value: int): self["start"] = value or 0

    @property
    def quantity(self): return self["quantity"]
    @quantity.setter
    def quantity(self, value: int): self["quantity"] = value or 0

    def output(self):
        if self.quantity <= 0:
            return ""
        return f' LIMIT {self.start}, {self.quantity}'
