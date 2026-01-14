from ......functions.decorators import parse_self_x_item_value_or_set_by_func
from ...nodes.tag import Tag


class Head(Tag):
    def __init__(self, u, attributes:dict[str, str|int|float|None]=None):
        Tag.__init__(self, u, None, attributes)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def title(self): return self.inner_after(-100).Title()

