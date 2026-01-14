from ..med import Med
from .....functions.decorators import parse_self_x_item_value, parse_self_x_item_value_or_set_by_func
from ....types.he import He


class Cls(He):
    def __init__(self, u, name: str):
        He.__init__(self, u)
        self.__x__['name'] = name

    @property
    @parse_self_x_item_value()
    def name(self): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def atrs(self): return {}

    def atr(self, name=None, value=None): self.atrs[name] = value
    def atr_px(self, name, value): self.atr(name, f'{value}px')

    def __str__(self):
        ls = []
        prefix = '\t' if isinstance(self.__u__, Med) else ''
        ls.append(f'{prefix}{self.name}{{')
        for n, v in self.atrs.items():
            ls.append(f'{prefix}\t{n}: {v};')
        ls.append(f'{prefix}}}')
        return '\n'.join(ls)
