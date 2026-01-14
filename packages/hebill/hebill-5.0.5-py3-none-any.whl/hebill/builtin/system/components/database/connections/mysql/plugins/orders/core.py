class Orders(dict):
    def __init__(self, orders=None):
        dict().__init__(self)
        self.adds(orders or {})

    def add(self, column, by=None):
        if column:
            self[column] = "DESC" if by is not None and by is not False and by.upper() == "DESC" else "ASC"

    def adds(self, orders):
        if orders:
            for k, v in orders.items():
                self.add(k, v)

    def output(self):
        if len(self) >= 1:
            return f" ORDER BY {", ".join(f'`{k}` {v}' for k, v in self.items())}"
        return ""
