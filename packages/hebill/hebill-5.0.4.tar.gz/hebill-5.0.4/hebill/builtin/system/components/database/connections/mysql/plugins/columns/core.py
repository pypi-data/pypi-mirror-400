class Columns(list):
    def __init__(self, columns=None):
        list.__init__(self)
        self.add(columns)

    def add(self, column):
        if isinstance(column, str) and column and column not in self:
            self.append(column.lower)
        elif isinstance(column, list):
            for c in column:
                self.add(c)

    def output(self):
        if len(self) < 1:
            return "*"
        return ", ".join(self)
