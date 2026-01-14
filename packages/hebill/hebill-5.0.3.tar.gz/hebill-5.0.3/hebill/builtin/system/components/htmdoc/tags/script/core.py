from ......functions.decorators import parse_self_x_item_value
from ...nodes.tag import Tag


class Script(Tag):
    def __init__(self, u, url=None, code=None, attributes:dict[str, str|int|float|None]=None):
        Tag.__init__(self, u, None, attributes)
        if url: self.attributes['src'] = url
        self.__x__['content'] = self.script(code)

    @property
    @parse_self_x_item_value()
    def content(self): return