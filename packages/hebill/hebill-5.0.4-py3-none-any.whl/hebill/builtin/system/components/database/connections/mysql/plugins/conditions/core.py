class Conditions(list):
    def __init__(self, logic=None, is_root=True):
        list.__init__(self)
        self._logic = 'AND' if logic is None or logic.upper == 'AND' else 'OR'
        self._is_root = is_root

    @property
    def is_root(self): return self._is_root
    @property
    def logic(self): return self._logic
    @logic.setter
    def logic(self, value): self._logic = 'AND' if value.upper == 'AND' else 'OR'
    def set_logic_and(self): self._logic = 'AND'
    def set_logic_or(self): self._logic = 'OR'

    def add(self, column, value, judge=None, logic=None, startwith=None, endwith=None):
        from .condition.core import Condition
        self.append(Condition(column, value, judge, logic, startwith, endwith))
        return self[-1]

    def add_and_equal(self, column, value): return self.add(column, value, "=", "AND")
    def add_or_equal(self, column, value): return self.add(column, value, "=", "OR")
    def add_and_not_equal(self, column, value): return self.add(column, value, "!=", "AND")
    def add_and_more_than(self, column, value): return self.add(column, value, ">", "AND")
    def add_and_not_more_than(self, column, value): return self.add(column, value, "<=", "AND")
    def add_and_less_than(self, column, value): return self.add(column, value, "<", "AND")
    def add_and_not_less_than(self, column, value): return self.add(column, value, ">=", "AND")

    def add_and_like(self, column, value, startwith=None, endwith=None):
        return self.add(column, value, "LIKE", "AND", startwith, endwith)

    def add_or_like(self, column, value, startwith=None, endwith=None):
        return self.add(column, value, "LIKE", "OR", startwith, endwith)

    def add_conditions(self, logic=None):
        self.append(Conditions(logic, False))
        return self[-1]

    def add_conditions_and(self): return self.add_conditions("AND")
    def add_conditions_or(self): return self.add_conditions("OR")

    def output(self, logic_bridge_requeried=False):
        s = ""
        for ss in self:
            s += ss.output(bool(s))
        if not s.strip():
            return ""

        if self.is_root:
            if not logic_bridge_requeried:
                return " " + s
            return f" {self.logic} ({s})"
        return f' WHERE{s}' if s else ""
