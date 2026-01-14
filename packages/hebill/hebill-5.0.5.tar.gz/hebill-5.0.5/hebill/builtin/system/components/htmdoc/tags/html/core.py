from ......functions.decorators import parse_self_x_item_value_or_set_by_func
from ...nodes.tag import Tag


class Html(Tag):
    def __init__(self, u, attributes:dict[str, str|int|float|None]=None):
        Tag.__init__(self, u, None, attributes)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def head(self): return self.inner_before1.Head()
    @property
    @parse_self_x_item_value_or_set_by_func()
    def body(self): return self.Body()
