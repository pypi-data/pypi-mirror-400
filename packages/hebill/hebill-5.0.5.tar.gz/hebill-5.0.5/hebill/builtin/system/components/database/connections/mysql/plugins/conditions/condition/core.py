class Condition(dict):
    def __init__(self, column, value, judge=None, logic=None, startwith=None, endwith=None):
        dict.__init__(self)
        self.update({
            "column": column,
            "value": value,
            "judge": '=' if judge is None else judge,
            "logic": 'AND' if logic is None or logic.upper == 'AND' else 'OR',
            "startwith": bool(startwith),
            "endwith": bool(endwith)
        })

    @property
    def column(self): return self["column"]
    @column.setter
    def column(self, value): self["column"] = value
    @property
    def value(self): return self["value"]
    @value.setter
    def value(self, _value): self["value"] = _value


    @property
    def judge(self): return self["judge"]
    @judge.setter
    def judge(self, value): self["judge"] = value
    def set_judge_equal(self): self.judge = '='
    def set_judge_un_equal(self): self.judge = '!='
    def set_judge_less_than(self): self.judge = '<'
    def set_judge_more_than(self): self.judge = '>'
    def set_judge_un_less_than(self): self.judge = '>='
    def set_judge_un_more_than(self): self.judge = '<='
    def set_judge_like(self): self.judge = 'LIKE'
    def set_judge_regexp(self): self.judge = 'REGEXP'
    # TODO 需要更新解析语言
    def set_judge_in_null(self): self.judge = 'IS NULL'
    # TODO 需要更新解析语言
    def set_judge_is_not_null(self): self.judge = 'IS NOT NULL'
    # TODO 需要更新解析语言
    def set_judge_in(self): self.judge = 'IN'
    # TODO 需要更新解析语言
    def set_judge_not_in(self): self.judge = 'NOT IN'
    # TODO 需要更新解析语言
    def set_judge_between_and(self): self.judge = 'BETWEEN AND'
    # TODO 需要更新解析语言
    def set_judge_spatial(self): self.judge = 'SPATIAL'
    # TODO 需要更新解析语言
    def set_judge_sounds_like(self): self.judge = 'SOUNDS LIKE'

    @property
    def logic(self): return self["logic"]
    @logic.setter
    def logic(self, value: str): self["logic"] = 'AND' if value.upper == 'AND' else 'OR',
    def set_logic_and(self): self["logic"] = 'AND'
    def set_logic_or(self): self["logic"] = 'OR'

    @property
    def startwith(self): return self["startwith"]
    @startwith.setter
    def startwith(self, value): self["startwith"] = value
    def set_startwith(self): self.startwith = True

    @property
    def endwith(self): return self["endwith"]
    @endwith.setter
    def endwith(self, value): self["endwith"] = value
    def set_endwith(self): self.endwith = True

    def output(self, logic_bridge_requeried=False):
        if not self.column:
            return " "
        s = f'`{self.column}` {self.judge} "'
        if self.judge == "LIKE" and not self.startwith:
            s += "%"
        s += str(self.value)
        if self.judge == "LIKE" and not self.endwith:
            s += "%"
        s += '"'
        if logic_bridge_requeried:
            s += " " + self.logic + " " + s
        return s
